from dotenv import load_dotenv
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory


# Importing the API opens the configured database, so the tests must never see the real one.
# This runs before that import, and load_dotenv does not override variables that are already set.
_directory: TemporaryDirectory = TemporaryDirectory(ignore_cleanup_errors=True)
environ["DATABASE_FILE"] = str(Path(_directory.name).joinpath("test.sqlite"))
environ["DATABASE_PASSWORD"] = "test"
load_dotenv(Path(__file__).parents[1].joinpath(".env.example"))
