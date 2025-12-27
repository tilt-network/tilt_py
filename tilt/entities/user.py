import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from tilt.types import Option, Some


@dataclass
class User:
    id: Option[UUID]
    name: str
    username: Option[str]
    email: Option[str]
    image: Option[str]
    phone: str
    role: Option[str]
    updated_at: Option[datetime]
    created_at: Option[datetime]

    @classmethod
    def from_json(cls, data: dict) -> "User":
        return cls(
            id=Some(UUID(data["id"])) if data.get("id") else None,
            name=data["name"],
            username=Some(data["username"]) if data.get("username") else None,
            email=Some(data["email"]) if data.get("email") else None,
            image=Some(data["image"]) if data.get("image") else None,
            phone=data["phone"],
            role=Some(data["role"]) if data.get("role") else None,
            updated_at=Some(
                datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            )
            if data.get("updated_at")
            else None,
            created_at=Some(
                datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            )
            if data.get("created_at")
            else None,
        )
