from apy.api import main as run_api
from apy.game import main as run_game
from argparse import ArgumentParser, Namespace


if __name__ == "__main__":
    argument_parser = ArgumentParser("APy: A minimalist Python application utilizing a FastAPI framework, with data storage managed by a SQLite database.")
    argument_parser.add_argument("--api", "-a", action="store_true", help="Run Web API service.")
    argument_parser.add_argument("--game", "-g", action="store_true", help="Process games.")
    arguments: Namespace = argument_parser.parse_args()

    if arguments.api:
        run_api()

    elif arguments.game:
        run_game()

    else:
        run_api()
