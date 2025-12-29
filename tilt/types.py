import json
from dataclasses import dataclass
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

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False


E = TypeVar("E")


@dataclass(frozen=True)
class Err(Generic[E], Exception):
    value: E

    def unwrap(self) -> NoReturn:
        raise RuntimeError(f"called unwrap() on Err: {self.value}")

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True


Result = Union[Ok[T], Err[E]]


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


class Environment(Enum):
    DEVELOPMENT = 0
    STAGING = 1
    PRODUCTION = 2


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Some):
            return o.value
        if isinstance(o, UUID):
            return str(o)
        if hasattr(o, "__json__"):
            return o.__json__()
        return super().default(o)
