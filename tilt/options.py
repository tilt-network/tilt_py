from tilt.source_handler import SourceHandler


class Options:

    def __init__(self, auth_token: str, data_src: SourceHandler, organization_id: str, program_id: str = None, **kwargs):
        self.__data_src = data_src
        self.__program_id = program_id
        self.__organization_id = organization_id
        self.__auth_token = auth_token

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
    def auth_token(self):
        return self.__auth_token

    @property
    def organization_id(self):
        return self.__organization_id
