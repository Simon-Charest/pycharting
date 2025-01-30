from pathlib import Path


DATA_PATH: Path = Path(__file__).parent.joinpath("data/**/*.json")
DATABASE_PATH: Path = Path(__file__).parent.joinpath("db")
EXCLUDE_REPRODUCTION: bool = True  # Exclude game reproductions.
EXCLUDE_UNOWNED: bool = True  # Exclude unowned games.
EXCLUDED_KEYS: list[str] = ["count"]
INCLUDED_KEYS: list[str] = ["min", "avg", "max", "sum"]
SANITIZE: bool = True  # Sanitize console and game names for PriceCharting.
SECONDS: float = 0.4  # Delay execution for a given number of seconds.
VERBOSE: bool = True  # View data during processing.
