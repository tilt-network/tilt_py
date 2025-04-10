import os
from typing_extensions import Optional


class Options:

    def __init__(self, api_key: Optional[str], data_src: Optional[str], program_id: Optional[str], **kwargs):
        self.__data_src = data_src
        self.__program_id = program_id
        if not api_key:
            self.__api_key = os.environ.get('TILT_API_KEY')
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
