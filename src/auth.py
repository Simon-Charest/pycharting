"""Accounts, passwords and sign-in sessions."""

from base64 import b64decode, b64encode
from hashlib import scrypt, sha256
from hmac import compare_digest
from secrets import token_bytes, token_urlsafe
from sqlcipher3.dbapi2 import Connection
from time import monotonic

from src.database import add_session, add_user, delete_session, delete_user, delete_user_sessions, get_session_user, get_user, get_users, set_user_password, set_user_role, update_user


ADMINISTRATOR: str = "administrator"  # Can change the collection
COLLABORATOR: str = "collaborator"  # Can only look at it
ROLES: tuple = (ADMINISTRATOR, COLLABORATOR)
SESSION_COOKIE: str = "pycharting_session"
SESSION_DAYS: int = 30
MAX_FAILURES: int = 5  # Failed sign-ins allowed for one account...
FAILURE_WINDOW: float = 15 * 60  # ...within this many seconds, after which it must wait that long

# scrypt's cost settings: about 16 MB of memory and a few dozen milliseconds per password
_N: int = 2 ** 14
_R: int = 8
_P: int = 1

_failures: dict = {}  # Lowercase account name -> times of its recent failed sign-ins


def hash_password(password: str) -> str:
    """A salted scrypt hash, with the settings needed to check it later."""

    salt: bytes = token_bytes(16)
    digest: bytes = scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)

    return f"scrypt${_N}${_R}${_P}${b64encode(salt).decode()}${b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        name, n, r, p, salt, digest = stored.split("$")
        expected: bytes = b64decode(digest)
        candidate: bytes = scrypt(password.encode(), salt=b64decode(salt), n=int(n), r=int(r), p=int(p), dklen=len(expected))
    except ValueError:
        return False

    return name == "scrypt" and compare_digest(candidate, expected)


# Checked against when the account does not exist, so that a wrong name takes as long as a wrong password
_UNKNOWN_USER_HASH: str = hash_password(token_urlsafe(16))


def create_account(connection: Connection, username: str, password: str, role: str = COLLABORATOR) -> bool:
    """Return False if that name is already taken."""

    _check_role(role)

    return add_user(connection, username.strip(), hash_password(password), role)


def change_password(connection: Connection, username: str, password: str) -> bool:
    """Return False if there is no such account."""

    return set_user_password(connection, username.strip(), hash_password(password))


def change_role(connection: Connection, username: str, role: str) -> bool:
    """Return False if there is no such account."""

    _check_role(role)

    return set_user_role(connection, username.strip(), role)


class SelfChange(Exception):
    """An administrator may not demote or delete their own account: the site could be left without one."""


def list_accounts(connection: Connection) -> list:
    return get_users(connection)


def update_account(connection: Connection, acting_id: int, id: int, role: str | None = None, password: str | None = None) -> bool:
    """Change another account's role, or any account's password; return False if there is no such account.

    A new password signs that account out everywhere, except for administrators changing their own.
    """

    if role is not None:
        _check_role(role)

        if id == acting_id and role != ADMINISTRATOR:
            raise SelfChange()

    if not update_user(connection, id, role, hash_password(password) if password else None):
        return False

    if password and id != acting_id:
        delete_user_sessions(connection, id)

    return True


def delete_account(connection: Connection, acting_id: int, id: int) -> bool:
    """Return False if there is no such account."""

    if id == acting_id:
        raise SelfChange()

    return delete_user(connection, id)


def _check_role(role: str) -> None:
    if role not in ROLES:
        raise ValueError("The role must be one of: " + ", ".join(ROLES) + ".")


def is_locked(username: str) -> bool:
    """Whether the account has failed to sign in too often lately."""

    key: str = username.strip().casefold()
    recent: list = [moment for moment in _failures.get(key, []) if monotonic() - moment < FAILURE_WINDOW]
    _failures[key] = recent

    return len(recent) >= MAX_FAILURES


def sign_in(connection: Connection, username: str, password: str) -> str | None:
    """Check the password and open a session; return the cookie's token, or None if refused."""

    user: dict | None = get_user(connection, username.strip())
    valid: bool = verify_password(password, user["password_hash"] if user else _UNKNOWN_USER_HASH)

    if not user or not valid:
        _failures.setdefault(username.strip().casefold(), []).append(monotonic())

        return None

    _failures.pop(username.strip().casefold(), None)
    token: str = token_urlsafe(32)
    add_session(connection, _token_hash(token), user["id"], SESSION_DAYS)

    return token


def session_user(connection: Connection, token: str | None) -> dict | None:
    """The name and role of the account signed in with that cookie, if its session is still valid."""

    return get_session_user(connection, _token_hash(token)) if token else None


def sign_out(connection: Connection, token: str | None) -> None:
    if token:
        delete_session(connection, _token_hash(token))


def _token_hash(token: str) -> str:
    """Sessions are stored by hash, so a copy of the database cannot be used to sign in."""

    return sha256(token.encode()).hexdigest()
