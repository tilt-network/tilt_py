from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from tilt.types import Option, Some


@dataclass
class Organization:
    id: Option[UUID]
    name: str
    image: Option[str]
    document: Option[str]
    scope: str
    document_type: Option[str]
    updated_at: Option[datetime]
    created_at: Option[datetime]

    @classmethod
    def from_json(cls, data: dict) -> "Organization":
        return cls(
            id=Some(UUID(data["id"])) if data.get("id") else None,
            name=data["name"],
            image=Some(data["image"]) if data.get("image") else None,
            document=Some(data["document"]) if data.get("document") else None,
            scope=data["scope"],
            document_type=Some(data["document_type"])
            if data.get("document_type")
            else None,
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
