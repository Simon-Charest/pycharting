from argparse import ArgumentParser, Namespace
from getpass import getpass
from sys import stdin


def read_password(from_stdin: bool) -> str:
    """Typed twice, or read from the first line of the standard input; never from the command line."""

    if from_stdin:
        password: str = stdin.readline().rstrip("\r\n")
    else:
        password = getpass("Password: ")

        if password != getpass("Password again: "):
            raise SystemExit("The passwords differ.")

    if not password:
        raise SystemExit("The password cannot be empty.")

    return password


def main() -> None:
    parser: ArgumentParser = ArgumentParser(prog="python .", description="PyCharting. Without a command, serves the collection page and its Web API.")
    commands = parser.add_subparsers(dest="command")
    add_user = commands.add_parser("add-user", help="create an account")
    add_user.add_argument("username")
    add_user.add_argument("--role", choices=("administrator", "collaborator"), default="collaborator", help="collaborators can only look (default); what is for sale needs no account at all")
    add_user.add_argument("--first-name")
    add_user.add_argument("--last-name")
    add_user.add_argument("--password-stdin", action="store_true", help="read the password from the standard input")
    set_password = commands.add_parser("set-password", help="change an account's password")
    set_password.add_argument("username")
    set_password.add_argument("--password-stdin", action="store_true", help="read the password from the standard input")
    set_role = commands.add_parser("set-role", help="make an account an administrator or a collaborator")
    set_role.add_argument("username")
    set_role.add_argument("role", choices=("administrator", "collaborator"))
    backup = commands.add_parser("backup", help="write a consistent copy of the database, even while the site runs")
    backup.add_argument("file")
    arguments: Namespace = parser.parse_args()

    if arguments.command is None:
        from src.api import run_api

        run_api()

        return

    from src.auth import change_password, change_role, create_account
    from pathlib import Path
    from src.database import backup_database, ensure_collection_schema, open_database

    connection = open_database()
    ensure_collection_schema(connection)

    if arguments.command == "backup":
        backup_database(connection, Path(arguments.file))
        connection.close()
        print(f"Database copied to {arguments.file}.")

        return

    if arguments.command == "add-user":
        done: bool = create_account(connection, arguments.username, read_password(arguments.password_stdin), arguments.role, arguments.first_name, arguments.last_name)
        message: str = f"{arguments.username} added as {arguments.role}." if done else f"{arguments.username} already exists."
    elif arguments.command == "set-password":
        done = change_password(connection, arguments.username, read_password(arguments.password_stdin))
        message = f"Password of {arguments.username} changed." if done else f"No account named {arguments.username}."
    else:
        done = change_role(connection, arguments.username, arguments.role)
        message = f"{arguments.username} is now {arguments.role}." if done else f"No account named {arguments.username}."

    connection.close()
    print(message)

    if not done:
        raise SystemExit(1)


# python . (from the project folder): serve the collection page and its Web API, or manage accounts
main()
