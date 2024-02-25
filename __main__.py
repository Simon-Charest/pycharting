from sqlite3 import Connection
from apy.api import main as run_api
from apy.game import get_connection, main as run_game, print_report
from argparse import ArgumentParser, Namespace


if __name__ == "__main__":
    argument_parser = ArgumentParser("APy: A minimalist Python application utilizing a FastAPI framework, with data storage managed by a SQLite database.")
    argument_parser.add_argument("--api", "-a", action="store_true", help="Run Web API service.")
    argument_parser.add_argument("--game", "-g", action="store_true", help="Process games.")
    argument_parser.add_argument("--report", "-r", action="store_true", help="Print game report.")
    arguments: Namespace = argument_parser.parse_args()

    if arguments.api:
        run_api()

    elif arguments.game or arguments.report:
        connection: Connection = get_connection()
        
        if arguments.game:
            run_game(connection)

        if arguments.report:
            print_report(connection)

        connection.close()

    else:
        argument_parser.print_help()
