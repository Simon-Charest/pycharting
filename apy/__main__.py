from argparse import ArgumentParser, Namespace
from pathlib import Path
from sqlite3 import Connection, connect

# APy
from api import run_api
from crawler import crawl_price_charting, execute, print_statistical_report, print_top_report
from utils import *


if __name__ == "__main__":
    argument_parser = ArgumentParser("APy: A minimalist Python application utilizing a FastAPI framework, with data storage managed by a SQLite database.")
    argument_parser.add_argument("--api", "-a", action="store_true", help="run Web API service")
    argument_parser.add_argument("--crawl", "-c", help="crawl PriceCharting, processing titles in a group (*: all)")
    argument_parser.add_argument("--delete", "-d", nargs=2, help="delete")
    argument_parser.add_argument("--report_statistical", "-s", action="store_true", help="print statistical report")
    argument_parser.add_argument("--report_top", "-t", help="print top X report")
    argument_parser.add_argument("--select_grouped", "--sg", help="select grouped")
    argument_parser.add_argument("--select_not_today", "--snt", action="store_true", help="select not today")
    arguments: Namespace = argument_parser.parse_args()

    connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))

    if arguments.api:
        run_api()

    if arguments.crawl:
        crawl_price_charting(connection, arguments.crawl)

    if arguments.delete:
        sql: str = Path(__file__).parent.joinpath("data/games/delete.sql").read_text()
        execute(connection, sql
            .replace("{CONSOLE_NAME}", arguments.delete[0])
            .replace("{PRODUCT_NAME}", arguments.delete[1]))

    if arguments.report_statistical:
        print_statistical_report(connection)

    if arguments.report_top:
        print_top_report(connection, arguments.report_top)

    if arguments.select_grouped:
        sql: str = Path(__file__).parent.joinpath("data/games/select_grouped.sql").read_text()
        rows: list = execute(connection, sql.replace("?", arguments.select_grouped))
        print_list(rows)

    if arguments.select_not_today:
        sql: str = Path(__file__).parent.joinpath("data/games/select_not_today.sql").read_text()
        rows: list = execute(connection, sql)
        print_list(rows)

    connection.close()
