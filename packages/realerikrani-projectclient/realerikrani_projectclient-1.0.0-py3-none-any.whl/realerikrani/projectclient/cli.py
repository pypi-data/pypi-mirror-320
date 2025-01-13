import argparse

from . import (
    create_new_key,
    create_project_with_key,
    delete_key,
    delete_project,
    read_keys,
    read_project,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for managing projects and keys.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_project_with_key.add_parser(subparsers)
    read_project.add_parser(subparsers)
    delete_project.add_parser(subparsers)
    create_new_key.add_parser(subparsers)
    read_keys.add_parser(subparsers)
    delete_key.add_parser(subparsers)

    args = parser.parse_args()
    # Call the appropriate function based on the command
    if hasattr(args, "func"):
        if args.command in ["delete", "read"]:
            args.func()  # Call without args
        else:
            args.func(args)  # Call with args for other commands
    else:
        parser.print_help()
