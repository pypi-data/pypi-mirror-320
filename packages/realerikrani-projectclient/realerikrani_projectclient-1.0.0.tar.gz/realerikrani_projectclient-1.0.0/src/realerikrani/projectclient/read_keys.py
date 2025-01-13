#!/usr/bin/env python
import argparse

from . import config


def run(args: argparse.Namespace) -> None:
    if args.parameter == "page_size":
        keys, token = config.create_project_client().read_keys(int(args.value))
    else:
        keys, token = config.create_project_client().read_keys(page_token=args.value)
    print(str(keys) + f"; next page token: {token}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("keys-read", help="Read public keys of a project.")
    parser.add_argument(
        "parameter",
        type=str,
        help="The kind of the request parameter",
        choices=["page_size", "page_token"],
    )
    parser.add_argument("value", help="The value of the request parameter")
    parser.set_defaults(func=run)
