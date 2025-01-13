#!/usr/bin/env python
import argparse

from . import config


def run() -> None:
    print(config.create_project_client().read())


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("read", help="Read a project.")
    parser.set_defaults(func=run)
