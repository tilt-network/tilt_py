from uuid import UUID

from tilt.source_handler import SourceHandler
from tilt.types import Option


class Options:
    def __init__(
        self,
        data_src: SourceHandler,
        program_id: Option[UUID] = None,
        secret_key: Option[str] = None,
        **kwargs,
    ):
        self.__data_src = data_src
        self.__program_id = program_id
        self.__secret_key = secret_key
        self.__auth_token: Option[str] = None
        self.__organization_id: Option[UUID] = None

    @property
    def data_src(self) -> SourceHandler:
        return self.__data_src

    @property
    def api_url(self) -> SourceHandler:
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
