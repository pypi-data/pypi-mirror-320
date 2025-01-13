from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class Project:
    id: UUID
    name: str

    @classmethod
    def make(cls: type["Project"], data: dict[str, Any]) -> "Project":
        return cls(id=UUID(data["id"]), name=data["name"])


@dataclass
class Key:
    id: UUID
    project_id: UUID
    pem: str
    created_at: datetime

    @classmethod
    def make(cls: type["Key"], data: dict[str, Any]) -> "Key":
        return cls(
            id=UUID(data["id"]),
            project_id=UUID(data["project_id"]),
            pem=data["pem"],
            created_at=data["created_at"],
        )
