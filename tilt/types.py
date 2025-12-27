import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Generic,
    NoReturn,
    TypeGuard,
    TypeVar,
    Union,
)
from uuid import UUID

S = TypeVar("S")


@dataclass
class Some(Generic[S]):
    value: S

    def __json__(self) -> S:
        return self.value

    def unwrap(self) -> S:
        return self.value


T = TypeVar("T")


@dataclass
class Ok(Generic[T]):
    value: T

    def unwrap(self) -> T:
        return self.value


E = TypeVar("E")


@dataclass(frozen=True)
class Err(Generic[E], Exception):
    value: E

    def unwrap(self) -> NoReturn:
        raise RuntimeError(f"called unwrap() on Err: {self.value}")


Result = Union[Ok[T], Err[E]]


def is_ok(result: Result[T, E]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)


def is_err(result: Result[T, E]) -> TypeGuard[Err[E]]:
    return isinstance(result, Err)


Option = Union[Some[T], None]


def is_some(value: Option[T]) -> TypeGuard[Some[T]]:
    return value is not None and isinstance(value, Some)


def is_none(value: Option[T]) -> bool:
    return value is None


def unwrap(value: Option[T]) -> T:
    if is_some(value):
        return value.value
    raise ValueError("Tried to unwrap None")


def unwrap_or(value: Option[T], default: T) -> T:
    if is_some(value):
        return value.value
    return default


# def unwrap_or_default(value: Option[T]) -> T:
#     if is_some(value):
#         return value.value
#     return


# def map_option(value: Option[T], func) -> Option[U]:
#     if is_some(value):
#         return Some(func(value.value))
#     return None


class ErrorKind(Enum):
    BAD_REQUEST = 0
    UNAUTHORIZED = 1
    FORBIDDEN = 2
    NOT_FOUND = 3
    INTERNAL_SERVER_ERROR = 4
    UNEXPECTED_STATUS_CODE = 5
    INVALID_RESPONSE = 6


@dataclass
class Error:
    # kind: ErrorKind
    message: str


# User


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


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Some):
            return o.value
        if isinstance(o, UUID):
            return str(o)
        if hasattr(o, "__json__"):
            return o.__json__()
        return super().default(o)
