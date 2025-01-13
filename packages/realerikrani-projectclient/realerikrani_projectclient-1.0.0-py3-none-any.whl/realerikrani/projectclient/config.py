import configparser
import os
import sys
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

import jwt
import requests

from realerikrani.baseclient import BaseAdapter, BaseClient

from .auth_jwt import JWTAuth
from .client import ProjectClient

_PUBLIC_KEY_PATH = "public"
_PRIVATE_KEY_PATH = "private"
_CURRENT_KID = "current_key_id"
_CURRENT_PID = "current_project_id"
_DEMO_INI = """
[DEFAULT]
url = http://localhost:5000
"""

sys.tracebacklimit = 0


def read_url(config: configparser.ConfigParser) -> str:
    result = config["DEFAULT"]["url"]
    parts = urlparse(result)
    if not (parts.scheme and parts.netloc):
        raise ValueError('["DEFAULT"]["url"] must have a valid URL of project API')
    return result


def read_config() -> tuple[configparser.ConfigParser, Path]:
    config = configparser.ConfigParser()
    config_path = Path(os.environ["PROJECT_CLI_CONFIG_PATH"])

    if not (
        config_path.exists()
        and config_path.is_file()
        and config_path.suffixes == [".ini"]
    ):
        raise ValueError("PROJECT_CLI_CONFIG_PATH must be an existing .ini file")

    config.read(config_path)

    try:
        read_url(config)
    except KeyError as k:
        raise ValueError(
            f"PROJECT_CLI_CONFIG_PATH file must have a URL of a project API {_DEMO_INI}"
        ) from k
    return config, config_path


def _write_config(config: configparser.ConfigParser, config_path: Path) -> None:
    with Path.open(config_path, "w") as configfile:
        config.write(configfile)


def read_project_and_key_id() -> tuple[UUID, UUID]:
    config, _ = read_config()
    default = config["DEFAULT"]
    return UUID(default[_CURRENT_PID]), UUID(default[_CURRENT_KID])


def create_key(
    public_path: str, private_path: str, *, project_id: UUID, kid: UUID
) -> None:
    config, config_path = read_config()

    section = str(kid) + "@" + str(project_id)
    config.add_section(section)
    config.set(section, _PUBLIC_KEY_PATH, public_path)
    config.set(section, _PRIVATE_KEY_PATH, private_path)
    config.set("DEFAULT", _CURRENT_KID, str(kid))
    config.set("DEFAULT", _CURRENT_PID, str(project_id))

    _write_config(config, config_path)


def read_private_key() -> str:
    config, _ = read_config()
    project_id, kid = read_project_and_key_id()
    section = str(kid) + "@" + str(project_id)
    try:
        with Path.open(Path(config.get(section, _PRIVATE_KEY_PATH))) as file:
            return file.read()
    except configparser.NoSectionError:
        msg = f"Key id {kid} not found for project id {project_id}"
        raise UserWarning(msg) from None


def delete_key(kid: UUID, project_id: UUID) -> None:
    config, config_path = read_config()
    project_id, _ = read_project_and_key_id()
    section = str(kid) + "@" + str(project_id)
    config.remove_section(section)
    _write_config(config, config_path)


def delete_keys(project_id: UUID) -> None:
    config, config_path = read_config()
    sections = config.sections()
    for section in sections:
        _, section_project_id = section.split("@")
        if UUID(section_project_id) == project_id:
            config.remove_section(section)
    config.remove_option("DEFAULT", _CURRENT_KID)
    config.remove_option("DEFAULT", _CURRENT_PID)
    _write_config(config, config_path)


def create_jwt(project_id: UUID, kid: UUID, private_key: str) -> str:
    return jwt.encode(
        payload={
            "iat": datetime.now(tz=UTC),
            "exp": datetime.now(tz=UTC) + timedelta(minutes=5),
            "iss": str(project_id),
        },
        key=private_key,
        algorithm="RS256",
        headers={"kid": str(kid)},
    )


def create_project_client() -> ProjectClient:
    config, _ = read_config()
    adapter = BaseAdapter()
    with requests.Session() as session:
        jwt_auth = None
        with suppress(KeyError):
            jwt_auth = JWTAuth(*read_project_and_key_id(), read_private_key())
        baseclient = BaseClient(
            session=session, adapter=adapter, url=read_url(config), auth=jwt_auth
        )
        return ProjectClient(baseclient)
