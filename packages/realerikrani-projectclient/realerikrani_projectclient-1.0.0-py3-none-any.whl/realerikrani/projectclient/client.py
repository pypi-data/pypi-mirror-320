from dataclasses import dataclass
from typing import Self
from uuid import UUID

from realerikrani.baseclient import BaseClient

from .model import Key, Project


@dataclass
class ProjectClient:
    http_client: BaseClient

    def create(self: Self, name: str, public_key: str) -> tuple[Project, UUID]:
        """Creates a project and associated with the provided public key.

        Args:
            name: The name of the project.
            public_key: Part of the management keypair.

        Returns:
            A tuple of the project and the registered key id
        """
        url = f"{self.http_client.url}/projects"

        response = self.http_client.post(
            url, data={"name": name, "public_key": public_key}, auth=None
        ).json()
        return Project.make(response["project"]), response["kid"]

    def read(self: Self) -> Project:
        """Reads the project specified in the auth jwt."""
        url = f"{self.http_client.url}/projects"
        response = self.http_client.get(url).json()
        return Project.make(response["project"])

    def delete(self: Self) -> Project:
        """Deletes the project specified in the auth jwt."""
        response = self.http_client.delete(f"{self.http_client.url}/projects")
        return Project.make(response.json()["project"])

    def create_key(self: Self, public_key: str) -> UUID:
        """Associates the provided public key with the project."""
        url = f"{self.http_client.url}/keys"
        response = self.http_client.post(url, data={"public_key": public_key}).json()
        return UUID(response["kid"])

    def read_keys(
        self: Self, page_size: int | None = None, page_token: str | None = None
    ) -> tuple[list[Key], str | None]:
        """Read keys of the project specified in the auth jwt.

        Next page token is None when no next page exists.
        Either page size or page token must be provided.

        Args:
            page_size: The amount of keys to fetch at a time.
            page_token: The encoded info for loading next page of keys.

        Returns:
            A tuple of the project and the registered key id
        """
        error = ValueError("provide either page_size or page_token")
        if page_size and page_token:
            raise error

        url = f"{self.http_client.url}/keys"
        if page_size:
            url += f"?page_size={page_size}"
        elif page_token:
            url += f"?page_token={page_token}"
        else:
            raise error

        response = self.http_client.get(url).json()
        return [Key.make(k) for k in response["keys"]], response["next_page_token"]

    def delete_key(self: Self, kid: UUID) -> UUID:
        """Deletes the provided public key association with the project."""
        url = f"{self.http_client.url}/keys/{kid}"
        response = self.http_client.delete(url).json()
        return UUID(response["kid"])
