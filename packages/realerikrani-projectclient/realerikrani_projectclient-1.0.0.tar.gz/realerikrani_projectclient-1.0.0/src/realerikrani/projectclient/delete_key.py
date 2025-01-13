#!/usr/bin/env python
import argparse
from uuid import UUID

from . import config


def run(args: argparse.Namespace) -> None:
    kid = args.id

    project_id, _ = config.read_project_and_key_id()

    deleted_kid = config.create_project_client().delete_key(kid)
    print(deleted_kid)
    config.delete_key(kid, project_id)


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("key-delete", help="Delete a key.")
    parser.add_argument("id", type=UUID, help="The key id to delete")

    parser.set_defaults(func=run)
