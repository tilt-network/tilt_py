from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from tilt.types import Option, Some


class JobStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELED = "canceled"


@dataclass
class Job:
    id: Option[UUID] = None
    organization_id: Option[UUID] = None
    program_id: Option[UUID] = None
    name: Option[str] = None
    status: Option[JobStatus] = None
    input_url: Option[str] = None
    output_url: Option[str] = None
    total_tokens: Option[int] = None
    total_tasks: Option[int] = None
    updated_at: Option[datetime] = None
    created_at: Option[datetime] = None
    completed_at: Option[datetime] = None
    in_progress_at: Option[datetime] = None
    expires_at: Option[datetime] = None
    failed_at: Option[datetime] = None
    expired_at: Option[datetime] = None

    @classmethod
    def from_json(cls, data: dict) -> "Job":
        return cls(
            id=Some(UUID(data["id"])) if data.get("id") else None,
            organization_id=Some(UUID(data["organization_id"]))
            if data.get("organization_id")
            else None,
            program_id=Some(UUID(data["program_id"]))
            if data.get("program_id")
            else None,
            name=Some(data["name"]) if data.get("name") else None,
            status=Some(JobStatus(data["status"])) if data.get("status") else None,
            input_url=Some(data["input_url"]) if data.get("input_url") else None,
            output_url=Some(data["output_url"]) if data.get("output_url") else None,
            total_tokens=Some(data["total_tokens"])
            if data.get("total_tokens") is not None
            else None,
            total_tasks=Some(data["total_tasks"])
            if data.get("total_tasks") is not None
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
            completed_at=Some(
                datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
            )
            if data.get("completed_at")
            else None,
            in_progress_at=Some(
                datetime.fromisoformat(data["in_progress_at"].replace("Z", "+00:00"))
            )
            if data.get("in_progress_at")
            else None,
            expires_at=Some(
                datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
            )
            if data.get("expires_at")
            else None,
            failed_at=Some(
                datetime.fromisoformat(data["failed_at"].replace("Z", "+00:00"))
            )
            if data.get("failed_at")
            else None,
            expired_at=Some(
                datetime.fromisoformat(data["expired_at"].replace("Z", "+00:00"))
            )
            if data.get("expired_at")
            else None,
        )
