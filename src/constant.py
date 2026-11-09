from dotenv import load_dotenv
from os import getenv
from pathlib import Path


# Settings live in .env (see .env.example). These only describe where the project's files are.
ROOT_PATH: Path = Path(__file__).parent.parent
SQL_PATH: Path = ROOT_PATH.joinpath("sql")
UI_PATH: Path = ROOT_PATH.joinpath("ui")

load_dotenv(ROOT_PATH.joinpath(".env"))


def _text(name: str) -> str:
    value: str | None = getenv(name)

    if value is None:
        raise ValueError(f"{name} must be set in .env (see .env.example).")

    return value


def _flag(name: str) -> bool:
    return _text(name).lower() == "true"


def _list(name: str) -> list[str]:
    """An optional comma-separated setting."""

    return [item.strip() for item in getenv(name, "").split(",") if item.strip()]


API_HOST: str = _text("API_HOST")
API_ORIGINS: list[str] = _list("API_ORIGINS")
API_PORT: int = int(_text("API_PORT"))
API_RELOAD: bool = _flag("API_RELOAD")
DATABASE_FILE: Path = ROOT_PATH.joinpath(_text("DATABASE_FILE"))
DATABASE_PASSWORD: str = _text("DATABASE_PASSWORD")
REQUEST_TIMEOUT: float = float(_text("REQUEST_TIMEOUT"))
