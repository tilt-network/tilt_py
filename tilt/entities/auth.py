from dataclasses import dataclass
from datetime import datetime

from tilt.entities.organization import Organization
from tilt.entities.user import User


@dataclass
class SkSignInResponse:
    token: str
    user: User
    organization: Organization
    expires_at: datetime

    @classmethod
    def from_json(cls, data: dict) -> "SkSignInResponse":
        return cls(
            token=data["token"],
            user=User.from_json(data["user"]),
            organization=Organization.from_json(data["organization"]),
            expires_at=datetime.fromisoformat(
                data["expires_at"].replace("Z", "+00:00")
            ),
        )
