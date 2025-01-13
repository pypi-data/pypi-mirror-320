#!/usr/bin/env python

import argparse

from . import config


def run() -> None:
    deleted_project = config.create_project_client().delete()
    print(deleted_project)
    config.delete_keys(deleted_project.id)


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("delete", help="Delete a project.")
    parser.set_defaults(func=run)
