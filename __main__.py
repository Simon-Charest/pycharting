from sqlite3 import Connection
from apy.api import main as run_api
from apy.game import get_connection, main as run_game, print_statistical_report, print_top_report
from argparse import ArgumentParser, Namespace


if __name__ == "__main__":
    argument_parser = ArgumentParser("APy: A minimalist Python application utilizing a FastAPI framework, with data storage managed by a SQLite database.")
    argument_parser.add_argument("--api", "-a", action="store_true", help="Run Web API service.")
    argument_parser.add_argument("--console_name", "-c", help="Process all games on a console.")
    argument_parser.add_argument("--report_statistical", "-s", action="store_true", help="Print statistical game report.")
    argument_parser.add_argument("--report_top", "-t", help="Print top game report.")
    arguments: Namespace = argument_parser.parse_args()

    if arguments.api:
        run_api()

    elif arguments.console_name or arguments.report_statistical or arguments.report_top:
        connection: Connection = get_connection()
        
        if arguments.console_name:
            run_game(connection, arguments.console_name)

        if arguments.report_statistical:
            print_statistical_report(connection)

        if arguments.report_top:
            print_top_report(connection, arguments.report_top)

        connection.close()

    else:
        argument_parser.print_help()
