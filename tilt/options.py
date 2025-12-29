import os
from typing import List
from uuid import UUID

from tilt.source_handler import SourceHandler
from tilt.types import Environment, Option


class Options:
    def __init__(
        self,
        data_src: Option[SourceHandler] = None,
        data: Option[List[bytes]] = None,
        program_id: Option[UUID] = None,
        secret_key: Option[str] = None,
        environment: Environment = Environment.PRODUCTION,
        **kwargs,
    ):
        self.__data_src = data_src
        self.__data = data
        self.__program_id = program_id
        self.__secret_key = secret_key
        self.__auth_token: Option[str] = None
        self.__organization_id: Option[UUID] = None
        self.environment = environment

    @property
    def data_src(self) -> Option[SourceHandler]:
        return self.__data_src

    @property
    def data(self) -> Option[List[bytes]]:
        return self.__data

    @property
    def api_url(self) -> Option[SourceHandler]:
        return self.__data_src

    @property
    def program_id(self) -> Option[UUID]:
        return self.__program_id

    @property
    def secret_key(self) -> Option[str]:
        return self.__secret_key

    @property
    def auth_token(self) -> Option[str]:
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, auth_token: Option[str]) -> None:
        self.__auth_token = auth_token

    @property
    def organization_id(self) -> Option[UUID]:
        return self.__organization_id

    @organization_id.setter
    def organization_id(self, organization_id: Option[UUID]) -> None:
        self.__organization_id = organization_id

    @property
    def base_url(self) -> str:
        if override := os.getenv("API_BASE_URL"):
            return override
        match self.environment:
            case Environment.PRODUCTION:
                return "https://production.tilt.rest"
            case Environment.DEVELOPMENT:
                return "https://development.tilt.rest"
            case Environment.STAGING:
                return "https://staging.tilt.rest"
