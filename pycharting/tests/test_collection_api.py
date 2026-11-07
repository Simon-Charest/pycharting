from pathlib import Path
from pytest import fixture, mark, raises
from fastapi import HTTPException
from sqlcipher3.dbapi2 import Connection

import pycharting.api as api
from pycharting.database import get_collection_entries, load_collection, open_database


@fixture
def connection(tmp_path: Path, monkeypatch) -> Connection:
    database: Connection = open_database(tmp_path.joinpath("test.sqlite"), "secret")
    load_collection(database)
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
        actual: list = await api.collection_entries()

        # Assert
        assert [(entry["kind"], entry["owner"], entry["console"], entry["title"]) for entry in actual] == [
            ("item", "Owner One", "Wii", "Zelda"),
            ("row", "Owner Two", "3DS", "Kid Icarus")
        ]
        assert actual[0]["values"]["virtual"] is True
        assert actual[0]["values"]["game"] == "43.98"
        assert "paid" not in actual[0]["values"]
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
    async def test_edited_item_reaches_the_crawler_data(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii U", name="Zelda 2"))

        # Assert
        assert load_collection(connection) == {"Wii U": [{"name": "Zelda 2"}]}

    @mark.asyncio
    async def test_add_item_for_chosen_owner_reaches_the_crawler_data(self, connection: Connection) -> None:
        # Act
        await api.add_collection_item(api.NewCollectionItem(owner_id=2, group_name="Wii", name="Mario", game=5))
        await api.add_collection_item(api.NewCollectionItem(owner_id=2, group_name="Wii", name="Metroid"))

        # Assert
        added: list = [entry for entry in get_collection_entries(connection) if entry["source"] == "added/Owner Two"]
        assert [(entry["owner"], entry["title"]) for entry in added] == [("Owner Two", "Mario"), ("Owner Two", "Metroid")]
        assert added[0]["values"]["game"] == 5
        assert {"name": "Mario"} in load_collection(connection)["Wii"]

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
        load_collection(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.execute("INSERT INTO collection_items (source_file_id, position, group_name, name) VALUES (1, 0, 'Wii', 'Zelda')")
        database.commit()

        for column in ("game", "manual", "box", "pricecharting"):
            database.execute(f"ALTER TABLE collection_items DROP COLUMN {column}")

        # Act
        actual: list = get_collection_entries(database)
        load_collection(database)  # A second run must not try to add them again.
        database.close()

        # Assert
        assert actual[0]["title"] == "Zelda"
        assert actual[0]["values"]["game"] is None
        assert actual[0]["values"]["pricecharting"] is None

    def test_older_database_gets_a_quantity_of_1_except_where_one_is_set(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        load_collection(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.executemany("INSERT INTO collection_items (source_file_id, position, group_name, name, quantity) VALUES (1, ?, 'Wii', ?, ?)", [(0, "One", None), (1, "Two", 2)])
        database.execute("INSERT INTO spreadsheet_rows (source_file_id, sheet, row_index, system, title) VALUES (1, 'Feuil2', 2, '3DS', 'Row')")
        database.commit()
        database.execute("ALTER TABLE spreadsheet_rows DROP COLUMN quantity")

        # Act
        entries: list = get_collection_entries(database)
        load_collection(database)  # A second run must find nothing left to do.
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
        load_collection(database)
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.execute("INSERT INTO spreadsheet_rows (source_file_id, sheet, row_index, system, title, amiibo) VALUES (1, 'Feuil2', 2, '3DS', 'Row', 'X')")
        database.commit()

        for column in ("gamepad", "previously_owned", "reproduction", '"virtual"'):
            database.execute(f"ALTER TABLE spreadsheet_rows DROP COLUMN {column}")

        # Act
        values: dict = get_collection_entries(database)[0]["values"]
        load_collection(database)  # A second run must find nothing left to do.
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

    @mark.asyncio
    async def test_crawler_still_gets_the_pal_console_name(self, connection: Connection) -> None:
        # Act
        await api.update_collection_item(1, api.CollectionItem(group_name="Wii", name="Zelda", region="PAL"))

        # Assert
        assert load_collection(connection) == {"PAL Wii": [{"name": "Zelda"}]}

    def test_older_database_moves_the_pal_prefix_into_the_region(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        load_collection(database)
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
        load_collection(database)  # A second run must find nothing left to do.
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

    def test_paid_values_move_to_game_and_the_column_is_removed(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        load_collection(database)
        database.execute("ALTER TABLE collection_items ADD COLUMN paid")
        database.execute("INSERT INTO owners (id, name) VALUES (1, 'A')")
        database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x'')")
        database.executemany(
            "INSERT INTO collection_items (source_file_id, position, group_name, name, paid, game) VALUES (1, ?, 'Wii', ?, ?, ?)",
            [(0, "Price", 12.5, None), (1, "Free", 0, None), (2, "Text", "43.98", None), (3, "Unpriced", None, None), (4, "Set by hand", 1, 9)]
        )
        database.commit()

        # Act
        entries: list = get_collection_entries(database)
        load_collection(database)  # A second run must find nothing left to do.
        columns: list = [row[1] for row in database.execute("PRAGMA table_info(collection_items)")]
        database.close()

        # Assert
        assert [entry["values"]["game"] for entry in entries] == [12.5, 0, "43.98", None, 9]
        assert "paid" not in columns

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
