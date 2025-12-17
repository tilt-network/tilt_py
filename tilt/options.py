from typing import Optional
from tilt.source_handler import SourceHandler


class Options:

    def __init__(self, data_src: SourceHandler, program_id: Optional[str] = None, secret_key: Optional[str] = None, **kwargs):
        self.__data_src = data_src
        self.__program_id = program_id
        self.__secret_key = secret_key
        self.__auth_token = ""
        self.__organization_id = ""

    @property
    def data_src(self):
        return self.__data_src

    @property
    def api_url(self):
        return self.__data_src

    @property
    def program_id(self):
        return self.__program_id

    @property
    def secret_key(self):
        return self.__secret_key

    @property
    def auth_token(self):
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, auth_token):
        self.__auth_token = auth_token

    @property
    def organization_id(self):
        return self.__organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        self.__organization_id = organization_id
