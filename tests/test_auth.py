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
    def test_without_session_the_page_leads_to_the_sign_in_form(self, client: TestClient) -> None:
        # Act
        response = client.get("/")

        # Assert
        assert (response.status_code, response.headers["location"]) == (303, "/login")
        assert client.get("/login").status_code == 200
        assert client.get("/docs").status_code == 303

    def test_without_session_the_collection_is_refused(self, client: TestClient) -> None:
        # Act and assert
        assert client.get("/collection/entries").status_code == 401
        assert client.delete("/collection/items/1").status_code == 401

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
        assert client.get("/auth/me").json() == {"username": ADMIN[0], "role": "administrator"}
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
        assert client.get("/collection/entries").status_code == 401

    def test_an_expired_session_is_refused(self, client: TestClient, connection: Connection) -> None:
        # Arrange
        sign_in(client, ADMIN)
        connection.execute("UPDATE sessions SET expires = DATETIME('now', '-1 minute')")
        connection.commit()

        # Act and assert
        assert client.get("/collection/entries").status_code == 401

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
