from dotenv import load_dotenv
from os import getenv
from pathlib import Path


# Settings live in .env (see .env.example). These two only describe where the code is.
ROOT_PATH: Path = Path(__file__).parent.parent
DATABASE_PATH: Path = Path(__file__).parent.joinpath("db")

load_dotenv(ROOT_PATH.joinpath(".env"))


def _text(name: str) -> str:
    value: str | None = getenv(name)

    if value is None:
        raise ValueError(f"{name} must be set in .env (see .env.example).")

    return value


def _flag(name: str) -> bool:
    return _text(name).lower() == "true"


def _list(name: str) -> list[str]:
    return [item.strip() for item in _text(name).split(",") if item.strip()]


API_HOST: str = _text("API_HOST")
API_PORT: int = int(_text("API_PORT"))
API_RELOAD: bool = _flag("API_RELOAD")
DATABASE_FILE: Path = ROOT_PATH.joinpath(_text("DATABASE_FILE"))
DATABASE_PASSWORD: str = _text("DATABASE_PASSWORD")
EXCLUDE_REPRODUCTION: bool = _flag("EXCLUDE_REPRODUCTION")
EXCLUDE_UNOWNED: bool = _flag("EXCLUDE_UNOWNED")
EXCLUDED_KEYS: list[str] = _list("EXCLUDED_KEYS")
INCLUDED_KEYS: list[str] = _list("INCLUDED_KEYS")
REQUEST_TIMEOUT: float = float(_text("REQUEST_TIMEOUT"))
SANITIZE: bool = _flag("SANITIZE")
SECONDS: float = float(_text("SECONDS"))
VERBOSE: bool = _flag("VERBOSE")
