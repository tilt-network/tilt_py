import os
from tilt.source_handler import SourceHandler


class Options:

    def __init__(self, api_key: str, data_src: SourceHandler = None, program_id: str = None, **kwargs):
        self.__data_src = data_src
        self.__program_id = program_id
        if api_key is None:
            self.__api_key = os.environ.get('TILT_API_KEY')
        else:
            self.__api_key = api_key

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
    def apikey(self):
        return self.__api_key
