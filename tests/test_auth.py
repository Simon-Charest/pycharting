from fastapi.testclient import TestClient
from pathlib import Path
from pytest import fixture, raises
from sqlcipher3.dbapi2 import Connection

import src.api as api
import src.auth as auth
from src.database import ensure_collection_schema, open_database


ADMIN: tuple = ("simon@example.com", "admin password")
VIEWER: tuple = ("viewer", "viewer password")


@fixture
def connection(tmp_path: Path, monkeypatch) -> Connection:
    database: Connection = open_database(tmp_path.joinpath("test.sqlite"), "secret")
    ensure_collection_schema(database)
    database.execute("INSERT INTO owners (id, name) VALUES (1, 'Owner One')")
    database.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a.json', '', x'')")
    database.execute("INSERT INTO collection_items (id, source_file_id, position, group_name, name) VALUES (1, 1, 0, 'Wii', 'Zelda')")
    database.commit()
    auth.create_account(database, *ADMIN, role=auth.ADMINISTRATOR)
    auth.create_account(database, *VIEWER)
    monkeypatch.setattr(api, "connection", database)
    monkeypatch.setattr(auth, "_failures", {})
    yield database
    database.close()


@fixture
def client(connection: Connection) -> TestClient:
    return TestClient(api.app, follow_redirects=False)


def sign_in(client: TestClient, account: tuple) -> None:
    response = client.post("/auth/login", json={"username": account[0], "password": account[1]})
    assert response.status_code == 200


class TestPasswords:
    def test_a_password_matches_only_its_own_hash(self) -> None:
        # Arrange
        stored: str = auth.hash_password("secret")

        # Act and assert
        assert auth.verify_password("secret", stored)
        assert not auth.verify_password("Secret", stored)
        assert "secret" not in stored

    def test_two_hashes_of_one_password_differ(self) -> None:
        # Act and assert
        assert auth.hash_password("secret") != auth.hash_password("secret")

    def test_a_damaged_hash_never_matches(self) -> None:
        # Act and assert
        assert not auth.verify_password("secret", "not a hash")

    def test_unknown_roles_are_refused(self, connection: Connection) -> None:
        # Act and assert
        with raises(ValueError):
            auth.create_account(connection, "someone", "password", role="owner")

    def test_names_are_unique_whatever_their_case(self, connection: Connection) -> None:
        # Act and assert
        assert not auth.create_account(connection, "VIEWER", "other")


class TestSignIn:
    def test_without_session_the_collection_page_still_opens(self, client: TestClient) -> None:
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        assert client.get("/login").status_code == 200
        assert client.get("/docs").status_code == 303  # Everything else still leads to the sign-in form
        assert client.get("/users").headers["location"] == "/login"

    def test_without_session_only_what_is_for_sale_is_served(self, client: TestClient) -> None:
        # Act and assert
        assert client.get("/collection/entries").status_code == 200  # Nothing for sale yet: an empty list
        assert client.get("/collection/entries").json() == []
        assert client.get("/collection/owners").status_code == 401
        assert client.delete("/collection/items/1").status_code == 401
        assert client.post("/collection/items", json={"owner_id": 1, "group_name": "Wii", "name": "Mario"}).status_code == 401

    def test_the_sign_in_page_needs_no_session(self, client: TestClient) -> None:
        # Act and assert
        assert client.get("/static/login.js").status_code == 200
        assert client.get("/static/collection.css").status_code == 200
        assert client.get("/health").status_code == 200

    def test_a_wrong_password_is_refused(self, client: TestClient) -> None:
        # Act
        response = client.post("/auth/login", json={"username": ADMIN[0], "password": "wrong"})

        # Assert
        assert (response.status_code, response.json()["detail"]) == (401, "invalid_credentials")
        assert auth.SESSION_COOKIE not in response.cookies

    def test_an_unknown_name_is_refused_the_same_way(self, client: TestClient) -> None:
        # Act
        response = client.post("/auth/login", json={"username": "nobody", "password": "wrong"})

        # Assert
        assert (response.status_code, response.json()["detail"]) == (401, "invalid_credentials")

    def test_signing_in_opens_the_collection(self, client: TestClient) -> None:
        # Act
        sign_in(client, (ADMIN[0].upper(), ADMIN[1]))

        # Assert
        assert client.get("/").status_code == 200
        assert client.get("/collection/entries").status_code == 200
        me: dict = client.get("/auth/me").json()
        assert (me["username"], me["role"], isinstance(me["id"], int)) == (ADMIN[0], "administrator", True)
        assert client.get("/login").headers["location"] == "/"

    def test_the_session_cookie_is_out_of_reach_of_scripts(self, client: TestClient) -> None:
        # Act
        response = client.post("/auth/login", json={"username": ADMIN[0], "password": ADMIN[1]})

        # Assert
        cookie: str = response.headers["set-cookie"].lower()
        assert "httponly" in cookie and "samesite=lax" in cookie and "secure" not in cookie

    def test_behind_https_the_cookie_is_secure(self, client: TestClient) -> None:
        # Act
        response = client.post("/auth/login", json={"username": ADMIN[0], "password": ADMIN[1]}, headers={"X-Forwarded-Proto": "https"})

        # Assert
        assert "secure" in response.headers["set-cookie"].lower()

    def test_signing_out_closes_the_session(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)
        token: str = client.cookies[auth.SESSION_COOKIE]

        # Act
        client.post("/auth/logout")
        client.cookies.set(auth.SESSION_COOKIE, token)  # Even a copy of the old cookie no longer works

        # Assert
        assert client.get("/auth/me").status_code == 401

    def test_an_expired_session_is_refused(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        sign_in(client, ADMIN)
        connection.execute("UPDATE sessions SET expires = DATETIME('now', '-1 minute')")
        connection.commit()

        # Act and assert
        assert client.get("/auth/me").status_code == 401

    def test_sessions_are_stored_by_hash(self, client: TestClient, connection: Connection) -> None:
        # Act
        sign_in(client, ADMIN)

        # Assert
        assert connection.execute("SELECT token_hash FROM sessions").fetchone()[0] != client.cookies[auth.SESSION_COOKIE]

    def test_too_many_failures_lock_the_account_for_a_while(self, client: TestClient) -> None:
        # Arrange
        for _ in range(auth.MAX_FAILURES):
            client.post("/auth/login", json={"username": ADMIN[0], "password": "wrong"})

        # Act
        response = client.post("/auth/login", json={"username": ADMIN[0], "password": ADMIN[1]})

        # Assert
        assert (response.status_code, response.json()["detail"]) == (429, "too_many_attempts")


class TestRoles:
    def test_a_collaborator_can_look(self, client: TestClient) -> None:
        # Act
        sign_in(client, VIEWER)

        # Assert
        assert client.get("/collection/entries").status_code == 200
        assert client.get("/auth/me").json()["role"] == "collaborator"

    def test_a_collaborator_cannot_change_anything(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        sign_in(client, VIEWER)

        # Act
        responses: list = [
            client.put("/collection/items/1", json={"group_name": "Wii", "name": "Changed"}),
            client.delete("/collection/items/1"),
            client.post("/collection/items", json={"owner_id": 1, "group_name": "Wii", "name": "New"}),
            client.post("/collection/items/1/prices")
        ]

        # Assert
        assert [(response.status_code, response.json()["detail"]) for response in responses] == [(403, "read_only")] * 4
        assert connection.execute("SELECT name FROM collection_items").fetchall() == [("Zelda",)]

    def test_an_administrator_can_change_the_collection(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        sign_in(client, ADMIN)

        # Act
        response = client.put("/collection/items/1", json={"group_name": "Wii", "name": "Changed"})

        # Assert
        assert response.status_code == 200
        assert connection.execute("SELECT name FROM collection_items").fetchone()[0] == "Changed"

    def test_a_role_can_change(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        auth.change_role(connection, VIEWER[0], auth.ADMINISTRATOR)
        sign_in(client, VIEWER)

        # Act and assert
        assert client.delete("/collection/items/1").status_code == 200


class TestUsers:
    def ids(self, client: TestClient) -> dict:
        return {user["username"]: user["id"] for user in client.get("/accounts").json()}

    def test_an_administrator_sees_the_accounts_without_their_passwords(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)

        # Act
        response = client.get("/accounts")

        # Assert
        assert client.get("/users").status_code == 200
        assert [(user["username"], user["role"]) for user in response.json()] == [(ADMIN[0], "administrator"), (VIEWER[0], "collaborator")]
        assert all(set(user) == {"id", "username", "first_name", "last_name", "role"} for user in response.json())

    def test_a_collaborator_cannot_see_the_accounts(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, VIEWER)

        # Act and assert
        assert (client.get("/users").status_code, client.get("/users").headers["location"]) == (303, "/")
        assert client.get("/accounts").status_code == 403
        assert client.post("/accounts", json={"username": "x", "role": "administrator", "password": "12345678"}).status_code == 403

    def test_without_session_the_accounts_are_refused(self, client: TestClient) -> None:
        # Act and assert
        assert client.get("/accounts").status_code == 401
        assert client.get("/users").headers["location"] == "/login"

    def test_an_administrator_adds_an_account_that_can_sign_in(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)

        # Act
        response = client.post("/accounts", json={"username": "newcomer", "role": "collaborator", "password": "a long password"})
        other: TestClient = TestClient(api.app, follow_redirects=False)

        # Assert
        assert response.status_code == 201
        assert other.post("/auth/login", json={"username": "newcomer", "password": "a long password"}).status_code == 200

    def test_names_cannot_be_taken_twice_and_passwords_must_be_long_enough(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)

        # Act and assert
        assert client.post("/accounts", json={"username": "Viewer", "role": "collaborator", "password": "a long password"}).json()["detail"] == "user_exists"
        assert client.post("/accounts", json={"username": "short", "role": "collaborator", "password": "1234567"}).status_code == 422

    def test_a_new_password_signs_the_account_out_everywhere(self, client: TestClient) -> None:
        # Arrange
        viewer: TestClient = TestClient(api.app, follow_redirects=False)
        sign_in(viewer, VIEWER)
        sign_in(client, ADMIN)

        # Act
        response = client.put(f"/accounts/{self.ids(client)[VIEWER[0]]}", json={"password": "a brand new one"})

        # Assert
        assert response.status_code == 200
        assert viewer.get("/auth/me").status_code == 401
        assert viewer.post("/auth/login", json={"username": VIEWER[0], "password": "a brand new one"}).status_code == 200

    def test_a_role_change_applies_at_once(self, client: TestClient) -> None:
        # Arrange
        viewer: TestClient = TestClient(api.app, follow_redirects=False)
        sign_in(viewer, VIEWER)
        sign_in(client, ADMIN)

        # Act
        client.put(f"/accounts/{self.ids(client)[VIEWER[0]]}", json={"role": "administrator"})

        # Assert
        assert viewer.get("/accounts").status_code == 200

    def test_an_administrator_cannot_demote_or_delete_themselves(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)
        own: int = self.ids(client)[ADMIN[0]]

        # Act
        responses: list = [client.put(f"/accounts/{own}", json={"role": "collaborator"}), client.delete(f"/accounts/{own}")]

        # Assert
        assert [(response.status_code, response.json()["detail"]) for response in responses] == [(409, "self")] * 2
        assert client.put(f"/accounts/{own}", json={"password": "my own new one"}).status_code == 200
        assert client.get("/accounts").status_code == 200  # Changing one's own password keeps one signed in

    def test_deleting_an_account_signs_it_out(self, client: TestClient) -> None:
        # Arrange
        viewer: TestClient = TestClient(api.app, follow_redirects=False)
        sign_in(viewer, VIEWER)
        sign_in(client, ADMIN)

        # Act
        response = client.delete(f"/accounts/{self.ids(client)[VIEWER[0]]}")

        # Assert
        assert response.status_code == 200
        assert viewer.get("/auth/me").status_code == 401
        assert VIEWER[0] not in self.ids(client)

    def test_unknown_accounts_are_not_found(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)

        # Act and assert
        assert client.put("/accounts/999", json={"role": "collaborator"}).status_code == 404
        assert client.delete("/accounts/999").status_code == 404

    def test_administrators_come_first_then_by_last_name(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        auth.create_account(connection, "zed", "a long password", auth.ADMINISTRATOR, "Zoé", "Arsenault")
        auth.create_account(connection, "amy", "a long password", auth.COLLABORATOR, "Amy", "Bérubé")
        auth.create_account(connection, "bob", "a long password", auth.COLLABORATOR, "Bob", "Arsenault")
        sign_in(client, ADMIN)

        # Act
        actual: list = [user["username"] for user in client.get("/accounts").json()]

        # Assert: last names first, accounts without one last, within each role
        assert actual == ["zed", ADMIN[0], "bob", "amy", VIEWER[0]]

    def test_names_are_added_changed_and_cleared(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)
        client.post("/accounts", json={"username": "newcomer", "first_name": " Jo ", "last_name": "Papin", "role": "collaborator", "password": "a long password"})
        id: int = self.ids(client)["newcomer"]
        named = lambda: next((user["first_name"], user["last_name"]) for user in client.get("/accounts").json() if user["id"] == id)

        # Act and assert
        assert named() == ("Jo", "Papin")
        client.put(f"/accounts/{id}", json={"first_name": "Jonathan", "last_name": "Papin"})
        assert named() == ("Jonathan", "Papin")
        client.put(f"/accounts/{id}", json={"role": "collaborator"})  # Names left out stay as they are
        assert named() == ("Jonathan", "Papin")
        client.put(f"/accounts/{id}", json={"first_name": "", "last_name": ""})
        assert named() == (None, None)

    def test_the_header_gets_the_signed_in_name(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        sign_in(client, ADMIN)
        client.put(f"/accounts/{self.ids(client)[ADMIN[0]]}", json={"first_name": "Simon", "last_name": "Charest"})

        # Act
        me: dict = client.get("/auth/me").json()

        # Assert
        assert (me["first_name"], me["last_name"]) == ("Simon", "Charest")

    def test_older_databases_gain_the_name_columns(self, tmp_path: Path) -> None:
        # Arrange
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.execute("ALTER TABLE users DROP COLUMN first_name")
        database.execute("ALTER TABLE users DROP COLUMN last_name")
        database.commit()

        # Act
        ensure_collection_schema(database)
        columns: list = [row[1] for row in database.execute("PRAGMA table_info(users)")]
        database.close()

        # Assert
        assert {"first_name", "last_name"} <= set(columns)


class TestBuyer:
    BUYER: tuple = ("retro", "buyer password")

    @fixture(autouse=True)
    def stock(self, connection: Connection) -> None:
        """Zelda is for sale, with what it was paid; Metroid is not for sale."""

        connection.execute("UPDATE collection_items SET selling = 1, paid = 12.5, owner_id = 1 WHERE id = 1")
        connection.execute("INSERT INTO collection_items (id, source_file_id, position, group_name, name, paid) VALUES (2, 1, 1, 'NES', 'Metroid', 30)")
        connection.commit()
        auth.create_account(connection, *self.BUYER, role=auth.BUYER)

    def test_a_buyer_only_sees_what_is_for_sale_without_what_it_was_paid(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, self.BUYER)

        # Act
        entries: list = client.get("/collection/entries").json()

        # Assert
        assert [(entry["title"], entry["values"]["paid"]) for entry in entries] == [("Zelda", None)]

    def test_a_visitor_with_no_account_sees_the_same_without_the_owner(self, client: TestClient) -> None:
        # Act: no sign-in at all
        entries: list = client.get("/collection/entries").json()

        # Assert
        assert [(entry["title"], entry["values"]["paid"]) for entry in entries] == [("Zelda", None)]
        assert [(entry["owner"], entry["source"], entry["values"]["owner_id"]) for entry in entries] == [(None, None, None)]

    def test_a_signed_in_account_is_told_who_owns_it(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, VIEWER)

        # Act
        entries: list = client.get("/collection/entries").json()

        # Assert
        assert [entry["owner"] for entry in entries if entry["title"] == "Zelda"] == ["Owner One"]

    def test_others_still_see_everything(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, VIEWER)

        # Act
        entries: list = client.get("/collection/entries").json()

        # Assert
        assert sorted((entry["title"], entry["values"]["paid"]) for entry in entries) == [("Metroid", 30), ("Zelda", 12.5)]

    def test_a_buyer_cannot_change_anything_nor_see_the_accounts(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, self.BUYER)

        # Act and assert
        assert client.put("/collection/items/1", json={"group_name": "Wii", "name": "Changed"}).status_code == 403
        assert client.post("/collection/items/1/prices").status_code == 403
        assert client.get("/accounts").status_code == 403

    def test_an_administrator_can_make_an_account_a_buyer(self, client: TestClient) -> None:
        # Arrange
        sign_in(client, ADMIN)
        id: int = next(account["id"] for account in client.get("/accounts").json() if account["username"] == VIEWER[0])

        # Act
        response = client.put(f"/accounts/{id}", json={"role": "buyer"})

        # Assert
        assert response.status_code == 200
        assert next(account["role"] for account in client.get("/accounts").json() if account["id"] == id) == "buyer"

    def test_older_databases_accept_buyers_and_keep_their_accounts(self, tmp_path: Path) -> None:
        # Arrange: a users table from before buyers, with an account and its session
        database: Connection = open_database(tmp_path.joinpath("old.sqlite"), "secret")
        ensure_collection_schema(database)
        database.executescript("""
            DROP TABLE users;
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE, password_hash TEXT NOT NULL,
                first_name TEXT, last_name TEXT, role TEXT NOT NULL DEFAULT 'collaborator' CHECK (role IN ('administrator', 'collaborator')));
            INSERT INTO users (id, username, password_hash, role) VALUES (7, 'simon', 'hash', 'administrator');
            INSERT INTO sessions (token_hash, user_id, expires) VALUES ('t', 7, '2999-01-01');
        """)

        # Act
        ensure_collection_schema(database)
        added: bool = auth.create_account(database, "retro", "buyer password", role=auth.BUYER)
        accounts: list = database.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
        sessions: list = database.execute("SELECT user_id FROM sessions").fetchall()
        database.close()

        # Assert
        assert added
        assert accounts[0] == (7, "simon", "administrator") and accounts[1][1:] == ("retro", "buyer")
        assert sessions == [(7,)]
