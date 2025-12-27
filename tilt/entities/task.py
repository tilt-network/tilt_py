from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from tilt.types import Option, Some


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELED = "canceled"


@dataclass
class Task:
    id: Option[UUID] = None
    job_id: Option[UUID] = None
    program_id: Option[UUID] = None
    segment_index: Option[int] = None
    status: Option[TaskStatus] = None
    result_url: Option[str] = None
    tokens_used: Option[int] = None
    size: Option[int] = None
    organization_id: Option[UUID] = None
    device_id: Option[UUID] = None
    started_at: Option[datetime] = None
    finished_at: Option[datetime] = None
    failed_at: Option[datetime] = None
    expires_at: Option[datetime] = None
    expired_at: Option[datetime] = None
    updated_at: Option[datetime] = None
    created_at: Option[datetime] = None

    @classmethod
    def from_json(cls, data: dict) -> "Task":
        return cls(
            id=Some(UUID(data["id"])) if data.get("id") else None,
            job_id=Some(UUID(data["job_id"])) if data.get("job_id") else None,
            program_id=Some(UUID(data["program_id"])) if data.get("program_id") else None,
            segment_index=Some(data["segment_index"]) if data.get("segment_index") is not None else None,
            status=Some(TaskStatus(data["status"])) if data.get("status") else None,
            result_url=Some(data["result_url"]) if data.get("result_url") else None,
            tokens_used=Some(data["tokens_used"]) if data.get("tokens_used") is not None else None,
            size=Some(data["size"]) if data.get("size") is not None else None,
            organization_id=Some(UUID(data["organization_id"])) if data.get("organization_id") else None,
            device_id=Some(UUID(data["device_id"])) if data.get("device_id") else None,
            started_at=Some(datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))) if data.get("started_at") else None,
            finished_at=Some(datetime.fromisoformat(data["finished_at"].replace("Z", "+00:00"))) if data.get("finished_at") else None,
            failed_at=Some(datetime.fromisoformat(data["failed_at"].replace("Z", "+00:00"))) if data.get("failed_at") else None,
            expires_at=Some(datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))) if data.get("expires_at") else None,
            expired_at=Some(datetime.fromisoformat(data["expired_at"].replace("Z", "+00:00"))) if data.get("expired_at") else None,
            updated_at=Some(datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))) if data.get("updated_at") else None,
            created_at=Some(datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))) if data.get("created_at") else None,
        )
