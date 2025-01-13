#!/usr/bin/env python
import argparse
from pathlib import Path

from . import config


def run(args: argparse.Namespace) -> None:
    name = args.name
    public_key_file = args.public_key_file
    private_key_file = args.private_key_file

    with Path.open(args.public_key_file) as pem1:
        public_key = pem1.read()

    project, kid = config.create_project_client().create(name, public_key)
    print(project, kid)

    config.create_key(
        str(public_key_file.resolve()),
        str(private_key_file.resolve()),
        project_id=project.id,
        kid=kid,
    )


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("create", help="Create a project with a key.")
    parser.add_argument("name", help="The name of the project")
    parser.add_argument(
        "public_key_file",
        type=Path,
        help="The path to RSA public key file in PEM format",
    )
    parser.add_argument(
        "private_key_file",
        type=Path,
        help="The path to RSA private key file in PEM format",
    )
    parser.set_defaults(func=run)
