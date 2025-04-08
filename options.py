import os


class Options:

    def __init__(self, api_key: str, data_src: str, program_id: str, **kwargs):
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
