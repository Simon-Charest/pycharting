from types import SimpleNamespace
from pathlib import Path
from pytest import fixture, mark, raises
from fastapi import HTTPException
from sqlcipher3.dbapi2 import Connection

import src.api as api
from src.database import ensure_collection_schema, get_collection_entries, open_database


@fixture
def connection(tmp_path: Path, monkeypatch) -> Connection:
    database: Connection = open_database(tmp_path.joinpath("test.sqlite"), "secret")
    ensure_collection_schema(database)
    database.execute("INSERT INTO owners (id, name) VALUES (1, 'Owner One'), (2, 'Owner Two')")
    database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'pycharting/data/jo/jo.json', '', x''), (2, 2, 'pycharting/data/video_games.xlsx', '', x'')")
    database.execute("INSERT INTO collection_items (id, source_file_id, position, group_name, name, game, 'virtual') VALUES (1, 1, 0, 'Wii', 'Zelda', '43.98', 1)")
    database.execute("INSERT INTO spreadsheet_rows (id, source_file_id, sheet, row_index, system, title, box) VALUES (1, 2, 'Feuil1', 2, '3DS', 'Kid Icarus', 'X')")
    database.commit()
    monkeypatch.setattr(api, "connection", database)
    yield database
    database.close()


class TestCollectionApi:
    @mark.asyncio
    async def test_entries_expose_owner_and_common_shape(self, connection: Connection) -> None:
        # Act
        actual: list = await api.collection_entries(SimpleNamespace(state=SimpleNamespace(user={"role": "administrator"})))

        # Assert
        assert [(entry["kind"], entry["owner"], entry["console"], entry["title"]) for entry in actual] == [
            ("item", "Owner One", "Wii", "Zelda"),
            ("row", "Owner Two", "3DS", "Kid Icarus")
        ]
        assert actual[0]["values"]["virtual"] is True
        assert actual[0]["values"]["game"] == "43.98"
        assert actual[0]["values"]["paid"] is None
        assert actual[1]["values"]["paid"] is None
        assert actual[1]["source"] == "pycharting/data/video_games.xlsx (Feuil1)"

    @mark.asyncio
    async def test_update_item_only_changes_that_item(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii U", name="Zelda 2", game=10.5, quantity=2))

        # Assert
        entries: list = get_collection_entries(connection)
        assert entries[0]["console"] == "Wii U"
        assert entries[0]["title"] == "Zelda 2"
        assert entries[0]["values"]["game"] == 10.5
        assert entries[0]["values"]["quantity"] == 2
        assert entries[0]["values"]["virtual"] is None
        assert entries[1]["title"] == "Kid Icarus"

    @mark.asyncio
    async def test_edited_item_is_saved(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii U", name="Zelda 2"))

        # Assert
        assert (get_collection_entries(connection)[0]["console"], get_collection_entries(connection)[0]["title"]) == ("Wii U", "Zelda 2")

    @mark.asyncio
    async def test_add_item_for_chosen_owner(self, connection: Connection) -> None:
        # Act
        await api.add_collection_item(api.NewCollectionItem(owner_id=2, group_name="Wii", name="Mario", game=5))
        await api.add_collection_item(api.NewCollectionItem(owner_id=2, group_name="Wii", name="Metroid"))

        # Assert
        added: list = [entry for entry in get_collection_entries(connection) if entry["source"] == "added/Owner Two"]
        assert [(entry["owner"], entry["title"]) for entry in added] == [("Owner Two", "Mario"), ("Owner Two", "Metroid")]
        assert added[0]["values"]["game"] == 5

    @mark.asyncio
    async def test_add_item_for_unknown_owner_returns_404(self, connection: Connection) -> None:
        # Act and assert
        with raises(HTTPException) as error:
            await api.add_collection_item(api.NewCollectionItem(owner_id=99, group_name="Wii", name="Mario"))

        assert error.value.status_code == 404
        assert len(get_collection_entries(connection)) == 2

    @mark.asyncio
    async def test_owners_are_listed(self, connection: Connection) -> None:
        # Act
        actual: list = await api.collection_owners()

        # Assert
        assert actual == [{"id": 1, "name": "Owner One"}, {"id": 2, "name": "Owner Two"}]

    @mark.asyncio
    async def test_item_keeps_game_manual_and_box_values(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", game=12.5, manual=0, box="X"))
        await api.add_collection_item(api.NewCollectionItem(owner_id=1, group_name="Wii", name="Mario", box=7))

        # Assert
        entries: list = get_collection_entries(connection)
        assert (entries[0]["values"]["game"], entries[0]["values"]["manual"], entries[0]["values"]["box"]) == (12.5, 0, "X")
        assert (entries[1]["values"]["game"], entries[1]["values"]["manual"], entries[1]["values"]["box"]) == (None, None, 7)

    def test_older_database_gets_the_new_columns_and_keeps_its_data(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.execute("INSERT INTO collection_items (source_file_id, position, group_name, name) VALUES (1, 0, 'Wii', 'Zelda')")
        database.commit()

        for column in ("game", "manual", "box", "pricecharting"):
            database.execute(f"ALTER TABLE collection_items DROP COLUMN {column}")

        # Act
        actual: list = get_collection_entries(database)
        ensure_collection_schema(database)  # A second run must not try to add them again.
        database.close()

        # Assert
        assert actual[0]["title"] == "Zelda"
        assert actual[0]["values"]["game"] is None
        assert actual[0]["values"]["pricecharting"] is None

    def test_older_database_gets_a_quantity_of_1_except_where_one_is_set(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.executemany("INSERT INTO collection_items (source_file_id, position, group_name, name, quantity) VALUES (1, ?, 'Wii', ?, ?)", [(0, "One", None), (1, "Two", 2)])
        database.execute("INSERT INTO spreadsheet_rows (source_file_id, sheet, row_index, system, title) VALUES (1, 'Feuil2', 2, '3DS', 'Row')")
        database.commit()
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN quantity")

        # Act
        entries: list = get_collection_entries(database)
        ensure_collection_schema(database)  # A second run must find nothing left to do.
        database.close()

        # Assert
        assert [entry["values"]["quantity"] for entry in entries] == [1, 2, 1]

    @mark.asyncio
    async def test_row_keeps_its_quantity_and_new_items_default_to_1(self, connection: Connection) -> None:
        # Act
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", quantity=3))
        await api.add_collection_item(api.NewCollectionItem(owner_id=1, group_name="Wii", name="Mario"))

        # Assert
        entries: list = get_collection_entries(connection)
        assert [entry["values"]["quantity"] for entry in entries if entry["title"] in ("Kid Icarus", "Mario")] == [1, 3]

    @mark.asyncio
    async def test_amiibo_and_console_are_tags_on_every_kind_of_entry(self, connection: Connection) -> None:
        # Arrange: the spreadsheet marked its tags with an X
        connection.execute("UPDATE spreadsheet_rows SET amiibo = 'X' WHERE id = 1")
        assert get_collection_entries(connection)[1]["values"]["amiibo"] is True

        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", amiibo=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", console=True))

        # Assert
        entries: list = get_collection_entries(connection)
        assert entries[0]["values"]["amiibo"] is True
        assert (entries[1]["values"]["console"], entries[1]["values"]["amiibo"]) == (True, None)

    @mark.asyncio
    async def test_spreadsheet_rows_accept_every_tag(self, connection: Connection) -> None:
        # Act
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", gamepad=True, previously_owned=True, reproduction=True, virtual=True))

        # Assert
        values: dict = get_collection_entries(connection)[1]["values"]
        assert (values["gamepad"], values["previously_owned"], values["reproduction"], values["virtual"]) == (True, True, True, True)
        assert values["console"] is None

    def test_older_database_rows_get_the_new_tags_empty(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.execute("INSERT INTO spreadsheet_rows (source_file_id, sheet, row_index, system, title, amiibo) VALUES (1, 'Feuil2', 2, '3DS', 'Row', 'X')")
        database.commit()

        for column in ("gamepad", "previously_owned", "reproduction", '"virtual"'):
            database.execute(f"ALTER TABLE spreadsheet_rows DROP COLUMN {column}")

        # Act
        values: dict = get_collection_entries(database)[0]["values"]
        ensure_collection_schema(database)  # A second run must find nothing left to do.
        database.close()

        # Assert
        assert values["amiibo"] is True
        assert values["virtual"] is None

    @mark.asyncio
    async def test_wishlist_is_a_tag_on_every_kind_of_entry(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", wishlist=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", wishlist=True))
        await api.add_collection_item(api.NewCollectionItem(owner_id=1, group_name="Wii", name="Mario", wishlist=True))

        # Assert
        assert [entry["values"]["wishlist"] for entry in get_collection_entries(connection)] == [True, True, True]

    @mark.asyncio
    async def test_region_owner_and_source_can_be_edited_on_every_kind_of_entry(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", region="PAL", owner_id=2, source="my list"))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", region="NTSC", owner_id=1, source="other list"))

        # Assert
        item, row = get_collection_entries(connection)
        assert (item["values"]["region"], item["owner"], item["source"]) == ("PAL", "Owner Two", "my list")
        assert (row["values"]["region"], row["owner"], row["source"]) == ("NTSC", "Owner One", "other list")

    @mark.asyncio
    async def test_leaving_owner_and_source_out_keeps_them(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda"))

        # Assert
        item: dict = get_collection_entries(connection)[0]
        assert (item["owner"], item["source"], item["values"]["owner_id"]) == ("Owner One", "pycharting/data/jo/jo.json", 1)

    @mark.asyncio
    async def test_unknown_owner_is_rejected_and_changes_nothing(self, connection: Connection) -> None:
        # Act and assert
        with raises(HTTPException):
            await api.update_collection_item(1, api.CollectionItem(group_name="Other", name="Other", owner_id=99))

        assert get_collection_entries(connection)[0]["title"] == "Zelda"

    def test_invalid_region_is_rejected(self) -> None:
        # Act and assert
        with raises(ValueError):
            api.CollectionItem(group_name="Wii", name="Zelda", region="Mars")

    def test_older_database_moves_the_pal_prefix_into_the_region(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.executemany(
            "INSERT INTO collection_items (source_file_id, position, group_name, name) VALUES (1, ?, ?, 'Game')",
            [(0, "PAL Wii"), (1, "Wii"), (2, "PC"), (3, "Nintendo Power")]
        )
        database.execute("INSERT INTO spreadsheet_rows (source_file_id, sheet, row_index, system, title) VALUES (1, 'Feuil2', 2, 'PAL Super Nintendo', 'Row')")
        database.commit()

        for table in ("collection_items", "spreadsheet_rows"):
            for column in ("region", "owner_id", "source"):
                database.execute(f"ALTER TABLE {table} DROP COLUMN {column}")

        # Act
        entries: list = get_collection_entries(database)
        ensure_collection_schema(database)  # A second run must find nothing left to do.
        database.close()

        # Assert
        assert [(entry["console"], entry["values"]["region"]) for entry in entries] == [
            ("Wii", "PAL"), ("Wii", "NTSC"), ("PC", None), ("Nintendo Power", None), ("Super Nintendo", "PAL")
        ]
        assert [entry["owner"] for entry in entries] == ["A"] * 5
        assert entries[4]["source"] == "a (Feuil2)"

    def test_negative_quantity_is_rejected(self) -> None:
        # Act and assert
        with raises(ValueError):
            api.SpreadsheetRow(system="3DS", title="Kid Icarus", quantity=-1)

    def test_paid_values_stay_apart_from_the_game(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.executemany(
            "INSERT INTO collection_items (source_file_id, position, group_name, name, paid, game) VALUES (1, ?, 'Wii', ?, ?, ?)",
            [(0, "Price", 12.5, None), (1, "Free", 0, 9)]
        )
        database.commit()

        # Act
        ensure_collection_schema(database)  # A later start must leave the paid values where they are.
        entries: list = get_collection_entries(database)
        database.close()

        # Assert
        assert [(entry["values"]["paid"], entry["values"]["game"]) for entry in entries] == [(12.5, None), (0, 9)]

    @mark.asyncio
    async def test_paid_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", paid=20))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", paid="5.50"))

        # Assert
        assert [entry["values"]["paid"] for entry in get_collection_entries(connection)] == [20, "5.50"]

    @mark.asyncio
    async def test_date_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", date="2026-11-08"))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", date="2025-01-31"))

        # Assert
        assert [entry["values"]["date"] for entry in get_collection_entries(connection)] == ["2026-11-08", "2025-01-31"]

    def test_date_must_be_yyyy_mm_dd(self) -> None:
        # Act and assert
        with raises(ValueError):
            api.CollectionItem(group_name="Wii", name="Zelda", date="08/11/2026")

    def test_older_databases_gain_the_date_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute('ALTER TABLE collection_items DROP COLUMN "date"')
        database.execute('ALTER TABLE spreadsheet_rows DROP COLUMN "date"')
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "date" in item_columns
        assert "date" in row_columns

    def test_older_databases_gain_the_paid_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE collection_items DROP COLUMN paid")
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN paid")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "paid" in item_columns
        assert "paid" in row_columns

    @mark.asyncio
    async def test_item_keeps_its_pricecharting_link(self, connection: Connection) -> None:
        # Arrange
        url: str = "https://www.pricecharting.com/game/wii/zelda"

        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", pricecharting=url))

        # Assert
        assert get_collection_entries(connection)[0]["values"]["pricecharting"] == url

    @mark.asyncio
    async def test_update_row(self, connection: Connection) -> None:
        # Act
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus Uprising", box=29.01))

        # Assert
        entry: dict = get_collection_entries(connection)[1]
        assert entry["title"] == "Kid Icarus Uprising"
        assert entry["values"]["box"] == 29.01

    @mark.asyncio
    async def test_delete_only_removes_that_entry(self, connection: Connection) -> None:
        # Act
        await api.delete_collection_item(1)

        # Assert
        assert [entry["kind"] for entry in get_collection_entries(connection)] == ["row"]

    @mark.asyncio
    @mark.parametrize("change", [
        lambda: api.delete_collection_item(99),
        lambda: api.delete_collection_row(99),
        lambda: api.update_collection_item(99, api.CollectionItem(group_name="Wii", name="Zelda"))
    ])
    async def test_missing_entry_returns_404(self, connection: Connection, change) -> None:
        # Act and assert
        with raises(HTTPException) as error:
            await change()

        assert error.value.status_code == 404

    def test_blank_required_field_and_unknown_field_are_rejected(self) -> None:
        # Act and assert
        with raises(ValueError):
            api.CollectionItem(group_name="Wii", name="   ")

        with raises(ValueError):
            api.CollectionItem(group_name="Wii", name="Zelda", unknown=1)

    def test_other_origins_are_not_allowed(self) -> None:
        # Arrange
        middleware = next(item for item in api.app.user_middleware if item.cls.__name__ == "CORSMiddleware")

        # Assert
        assert "*" not in middleware.kwargs["allow_origins"]


PRODUCT_PAGE: str = """<h1 id="product_name">Zelda</h1><div id="full-prices"><table>
<tr><td>Loose</td><td>$1,043.50</td></tr><tr><td>Box Only</td><td>$12.00</td></tr><tr><td>Manual Only</td><td>-</td></tr>
</table></div>"""


class FakeResponse:
    def __init__(self, url: str, text: str, status_code: int = 200, headers: dict | None = None) -> None:
        self.url, self.text, self.status_code, self.ok = url, text, status_code, status_code < 400
        self.headers = headers or {}


class TestPrices:
    @fixture(autouse=True)
    def rate(self, monkeypatch) -> list:
        """A fixed rate, and no real waiting: the waits asked for are recorded instead."""

        import src.prices as prices
        waits: list = []
        monkeypatch.setattr(prices, "usd_cad_rate", lambda: 1.5)
        monkeypatch.setattr(prices, "sleep", waits.append)
        monkeypatch.setattr(prices, "_last_request", float("-inf"))
        monkeypatch.setattr(prices, "_paused_until", float("-inf"))

        return waits

    def test_requests_are_spaced(self, monkeypatch, rate: list) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE))

        # Act
        prices.fetch_prices("https://p/game/wii/zelda", "Zelda", "Wii", None)
        prices.fetch_prices("https://p/game/wii/zelda", "Zelda", "Wii", None)

        # Assert
        assert len(rate) == 1 and prices.MIN_INTERVAL - 0.5 < rate[0] <= prices.MIN_INTERVAL

    def test_a_429_waits_as_asked_then_tries_once_more(self, monkeypatch, rate: list) -> None:
        # Arrange
        import src.prices as prices
        answers: list = [FakeResponse("", "", 429, {"Retry-After": "7"}), FakeResponse("https://p/game/wii/zelda", PRODUCT_PAGE)]
        monkeypatch.setattr(prices, "get", lambda url, **_: answers.pop(0))

        # Act
        actual: dict = prices.fetch_prices("https://p/game/wii/zelda", "Zelda", "Wii", None)

        # Assert
        assert actual["game"] == 1565.25
        assert 7.0 in rate

    def test_a_second_429_stops_asking_for_a_while(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        calls: list = []
        monkeypatch.setattr(prices, "get", lambda url, **_: calls.append(url) or FakeResponse(url, "", 429, {"Retry-After": "5"}))

        # Act and assert
        with raises(prices.RateLimited):
            prices.fetch_prices("https://p/game/wii/zelda", "Zelda", "Wii", None)

        with raises(prices.RateLimited):
            prices.fetch_prices("https://p/game/wii/metroid", "Metroid", "Wii", None)

        assert len(calls) == 2

    def test_a_429_asking_for_a_long_wait_is_not_retried(self, monkeypatch, rate: list) -> None:
        # Arrange
        import src.prices as prices
        calls: list = []
        monkeypatch.setattr(prices, "get", lambda url, **_: calls.append(url) or FakeResponse(url, "", 429, {"Retry-After": "3600"}))

        # Act and assert
        with raises(prices.RateLimited):
            prices.fetch_prices("https://p/game/wii/zelda", "Zelda", "Wii", None)

        assert len(calls) == 1 and 3600.0 not in rate

    def test_product_page_gives_a_price_for_each_part_in_cad(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE))

        # Act
        actual: dict = prices.fetch_prices("https://www.pricecharting.com/game/wii/zelda", "Zelda", "Wii", None)

        # Assert
        assert actual == {"url": "https://www.pricecharting.com/game/wii/zelda", "game": 1565.25, "manual": None, "box": 18.0}

    def test_search_picks_the_result_with_exactly_that_title(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table"><tr><td class="title"><a href="https://p/game/pal-wii/zelda-ii">Zelda II</a></td></tr>
        <tr><td class="title"><a href="https://p/game/pal-wii/zelda">Zelda</a></td></tr></table>"""
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE if url == "https://p/game/pal-wii/zelda" else search))

        # Act
        actual: dict = prices.fetch_prices(None, "zelda", "Wii", "PAL")

        # Assert
        assert actual["url"] == "https://p/game/pal-wii/zelda"

    def test_search_keeps_the_entrys_system_and_standard(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table">
        <tr><td class="title"><a href="https://p/game/nes/castlevania">Castlevania</a></td></tr>
        <tr><td class="title"><a href="https://p/game/pal-gameboy-advance/castlevania">Castlevania</a></td></tr>
        <tr><td class="title"><a href="https://p/game/pal-nes/castlevania">Castlevania</a></td></tr></table>"""
        requested: list = []
        monkeypatch.setattr(prices, "get", lambda url, **_: requested.append(url) or FakeResponse(url, PRODUCT_PAGE if "/game/" in url else search))

        # Act
        actual: dict = prices.fetch_prices(None, "Castlevania", "NES", "PAL")

        # Assert
        assert actual["url"] == "https://p/game/pal-nes/castlevania"
        assert requested[0] == prices.SEARCH_URL + "Castlevania%20pal%20nes"

    def test_titles_match_without_punctuation_accents_or_a_leading_the(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table">
        <tr><td class="title"><a href="https://p/game/super-nintendo/zelda-link-to-the-past">Zelda Link to the Past</a></td></tr>
        <tr><td class="title"><a href="https://p/game/nes/castlevania-ii-simon%27s-quest">Castlevania II Simon's Quest</a></td></tr></table>"""
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE if "/game/" in url else search))

        # Act
        actual: dict = prices.fetch_prices(None, "Castlevania II: Simon’s Quest", "NES", "NTSC")

        # Assert
        assert actual["url"] == "https://p/game/nes/castlevania-ii-simon%27s-quest"

    def test_a_variant_in_brackets_is_a_last_resort(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table">
        <tr><td class="title"><a href="https://p/game/pal-super-nintendo/super-mario-world-yellow-box">Super Mario World [Yellow Box]</a></td></tr></table>"""
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE if "/game/" in url else search))

        # Act
        actual: dict = prices.fetch_prices(None, "Super Mario World", "SNES", "PAL")

        # Assert
        assert actual["url"] == "https://p/game/pal-super-nintendo/super-mario-world-yellow-box"

    def test_a_stored_link_for_another_standard_is_replaced(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table"><tr><td class="title"><a href="https://p/game/pal-nes/metroid">Metroid</a></td></tr></table>"""
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE if "/game/" in url else search))

        # Act
        actual: dict = prices.fetch_prices("https://p/game/nes/metroid", "Metroid", "NES", "PAL")

        # Assert
        assert actual["url"] == "https://p/game/pal-nes/metroid"

    def test_without_a_standard_a_stored_link_for_any_standard_is_kept(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE))

        # Act
        actual: dict = prices.fetch_prices("https://p/game/pal-nes/castlevania", "Castlevania", "NES", None)

        # Assert
        assert actual["url"] == "https://p/game/pal-nes/castlevania"

    def test_a_stored_link_for_another_system_is_replaced(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        search: str = """<table id="games_table"><tr><td class="title"><a href="https://p/game/nes/castlevania">Castlevania</a></td></tr></table>"""
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE if "/game/" in url else search))

        # Act
        actual: dict = prices.fetch_prices("https://p/game/gameboy/castlevania-adventure", "Castlevania", "NES", None)

        # Assert
        assert actual["url"] == "https://p/game/nes/castlevania"

    def test_a_stored_link_to_another_kind_of_product_is_kept(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, PRODUCT_PAGE))

        # Act
        actual: dict = prices.fetch_prices("https://p/game/amiibo/peach-wedding-outfit", "Peach (Wedding Outfit)", "Switch", None)

        # Assert
        assert actual["url"] == "https://p/game/amiibo/peach-wedding-outfit"

    def test_a_european_genesis_is_a_pal_mega_drive(self) -> None:
        # Arrange
        import src.prices as prices

        # Act and assert
        assert prices.console_slug("Sega Genesis", "PAL") == "pal-sega-mega-drive"

    def test_a_direct_hit_for_another_standard_is_not_taken(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse("https://p/game/nes/metroid", PRODUCT_PAGE))

        # Act and assert
        with raises(prices.ProductNotFound):
            prices.fetch_prices(None, "Metroid", "NES", "PAL")

    def test_systems_that_name_their_standard(self) -> None:
        # Arrange
        import src.prices as prices

        # Act
        actual: list = [prices.console_slug("Super Famicom", "NTSC"), prices.console_slug("Sega Mega Drive", None), prices.console_slug("Nintendo Game Boy Color", "PAL"), prices.console_slug("Nintendo Power", None)]

        # Assert
        assert actual == ["super-famicom", "pal-sega-mega-drive", "pal-gameboy-color", None]

    def test_search_without_that_title_finds_nothing(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        monkeypatch.setattr(prices, "get", lambda url, **_: FakeResponse(url, "<table id='games_table'></table>"))

        # Act and assert
        with raises(prices.ProductNotFound):
            prices.fetch_prices(None, "Zelda", "Wii", None)


class TestUpdatePrices:
    @mark.asyncio
    async def test_only_owned_parts_are_refreshed_and_dated(self, connection: Connection, monkeypatch) -> None:
        # Arrange
        connection.execute("UPDATE collection_items SET box = 'X' WHERE id = 1")
        connection.commit()
        monkeypatch.setattr(api, "fetch_prices", lambda *_: {"url": "https://p/zelda", "game": 50.0, "manual": 9.0, "box": None})

        # Act
        await api.update_entry_prices("items", 1)
        values: dict = get_collection_entries(connection)[0]["values"]

        # Assert
        assert (values["game"], values["manual"], values["box"], values["pricecharting"]) == (50.0, None, "X", "https://p/zelda")
        assert values["date"] == api.date.today().isoformat()

    @mark.asyncio
    async def test_a_row_is_refreshed_too(self, connection: Connection, monkeypatch) -> None:
        # Arrange
        monkeypatch.setattr(api, "fetch_prices", lambda *_: {"url": "https://p/kid-icarus", "game": 1.0, "manual": 2.0, "box": 3.0})

        # Act
        await api.update_entry_prices("rows", 1)
        values: dict = get_collection_entries(connection)[1]["values"]

        # Assert
        assert (values["game"], values["manual"], values["box"]) == (None, None, 3.0)

    @mark.asyncio
    async def test_nothing_owned_is_refused(self, connection: Connection) -> None:
        # Arrange
        connection.execute("UPDATE collection_items SET game = NULL WHERE id = 1")
        connection.commit()

        # Act and assert
        with raises(HTTPException) as error:
            await api.update_entry_prices("items", 1)

        assert error.value.detail == "nothing_owned"

    @mark.asyncio
    async def test_pricecharting_refusing_requests_is_a_429(self, connection: Connection, monkeypatch) -> None:
        # Arrange
        import src.prices as prices

        def refuse(*_) -> dict:
            raise prices.RateLimited()

        monkeypatch.setattr(api, "fetch_prices", refuse)

        # Act and assert
        with raises(HTTPException) as error:
            await api.update_entry_prices("items", 1)

        assert (error.value.status_code, error.value.detail) == (429, "rate_limited")

    @mark.asyncio
    async def test_missing_entry_is_not_found(self, connection: Connection) -> None:
        # Act and assert
        with raises(HTTPException) as error:
            await api.update_entry_prices("items", 99)

        assert error.value.status_code == 404


class TestExchangeRate:
    def test_rate_comes_from_the_bank_of_canada_once_a_day(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices
        calls: list = []

        class Rate:
            def raise_for_status(self) -> None: pass
            def json(self) -> dict: return {"observations": [{"d": "2026-11-06", "FXUSDCAD": {"v": "1.4113"}}]}

        monkeypatch.setattr(prices, "_rates", {})
        monkeypatch.setattr(prices, "get", lambda url, **_: calls.append(url) or Rate())

        # Act
        actual: list = [prices.usd_cad_rate(), prices.usd_cad_rate()]

        # Assert
        assert actual == [1.4113, 1.4113]
        assert calls == [prices.RATE_URL]

    def test_missing_rate_is_an_error(self, monkeypatch) -> None:
        # Arrange
        import src.prices as prices

        class Empty:
            def raise_for_status(self) -> None: pass
            def json(self) -> dict: return {"observations": []}

        monkeypatch.setattr(prices, "_rates", {})
        monkeypatch.setattr(prices, "get", lambda url, **_: Empty())

        # Act and assert
        with raises(prices.ExchangeRateError):
            prices.usd_cad_rate()


class TestAccessory:
    @mark.asyncio
    async def test_accessory_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", accessory=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", accessory=True))

        # Assert
        assert [entry["values"]["accessory"] for entry in get_collection_entries(connection)] == [True, True]

    def test_older_databases_gain_the_accessory_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE collection_items DROP COLUMN accessory")
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN accessory")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "accessory" in item_columns
        assert "accessory" in row_columns


class TestDamaged:
    @mark.asyncio
    async def test_damaged_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", damaged=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", damaged=True))

        # Assert
        assert [entry["values"]["damaged"] for entry in get_collection_entries(connection)] == [True, True]

    def test_older_databases_gain_the_damaged_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE collection_items DROP COLUMN damaged")
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN damaged")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "damaged" in item_columns
        assert "damaged" in row_columns


class TestSelling:
    @mark.asyncio
    async def test_selling_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", selling=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", selling=True))

        # Assert
        assert [entry["values"]["selling"] for entry in get_collection_entries(connection)] == [True, True]

    def test_older_databases_gain_the_selling_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE collection_items DROP COLUMN selling")
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN selling")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "selling" in item_columns
        assert "selling" in row_columns

    def test_the_duplicate_column_becomes_selling_with_its_values(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)

        for table in ("collection_items", "spreadsheet_rows"):
            database.execute(f"ALTER TABLE {table} RENAME COLUMN selling TO duplicate")

        database.execute("INSERT INTO owners (name) VALUES ('Simon')")
        database.execute("INSERT INTO source_files (owner_id, path, sha256, content) VALUES (1, 'old.json', '', x'')")
        database.execute("INSERT INTO collection_items (source_file_id, position, group_name, name, duplicate) VALUES (1, 0, 'NES', 'Zelda', 1)")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        selling: list = [row[0] for row in database.execute("SELECT selling FROM collection_items")]
        database.close()

        # Assert
        assert "selling" in item_columns and "duplicate" not in item_columns
        assert "selling" in row_columns and "duplicate" not in row_columns
        assert selling == [1]


class TestBuying:
    @mark.asyncio
    async def test_buying_is_saved_on_items_and_rows(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", buying=True))
        await api.update_collection_row(1, api.SpreadsheetRow(system="3DS", title="Kid Icarus", buying=True))

        # Assert
        assert [entry["values"]["buying"] for entry in get_collection_entries(connection)] == [True, True]

    def test_older_databases_gain_the_buying_column(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE collection_items DROP COLUMN buying")
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN buying")
        database.commit()

        # Act
        ensure_collection_schema(database)
        item_columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        row_columns: list = [row[1] for row in database.execute("PRAGMA table_info(spreadsheet_rows)")]
        database.close()

        # Assert
        assert "buying" in item_columns
        assert "buying" in row_columns
