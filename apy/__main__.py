from argparse import ArgumentParser, Namespace
from pathlib import Path
from sqlite3 import Connection, connect

# APy
from api import run_api
from crawler import crawl_price_charting, print_statistical_report, print_top_report


if __name__ == "__main__":
    argument_parser = ArgumentParser("APy: A minimalist Python application utilizing a FastAPI framework, with data storage managed by a SQLite database.")
    argument_parser.add_argument("--api", "-a", action="store_true", help="Run Web API service.")
    argument_parser.add_argument("--crawl", "-c", help="Crawl PriceCharting, processing titles in a group (*: all).")
    argument_parser.add_argument("--report_statistical", "-s", action="store_true", help="Print statistical report.")
    argument_parser.add_argument("--report_top", "-t", help="Print top X report.")
    arguments: Namespace = argument_parser.parse_args()

    connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))

    if arguments.api:
        run_api()

    if arguments.crawl:
        crawl_price_charting(connection, arguments.crawl)

    if arguments.report_statistical:
        print_statistical_report(connection)

    if arguments.report_top:
        print_top_report(connection, arguments.report_top)

    connection.close()
