#!/usr/bin/env python
import argparse
from pathlib import Path

from . import config


def run(args: argparse.Namespace) -> None:
    public_key_file = args.public_key_file
    private_key_file = args.private_key_file

    with Path.open(public_key_file) as pem1:
        public_key = pem1.read()

    project_id, _ = config.read_project_and_key_id()

    created_kid = config.create_project_client().create_key(public_key)
    print(created_kid)

    config.create_key(
        str(public_key_file.resolve()),
        str(private_key_file.resolve()),
        project_id=project_id,
        kid=created_kid,
    )


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("key-create", help="Create a new key for a project.")
    parser.add_argument(
        "public_key_file",
        type=Path,
        help="The path to RSA public key file in PEM format",
    )
    parser.add_argument(
        "private_key_file",
        type=Path,
        help="The path RSA private key file in PEM format",
    )

    parser.set_defaults(func=run)
