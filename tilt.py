from options import Options
from connection import Connection
import asyncio


class Tilt:

    def __init__(self, data_src: str = None, program_id: str = None, options: Options = None):
        self.__options = options
        if not options:
            self.__options = Options(data_src, program_id)
        self.__conn = Connection(self.__options.data_src, self.__options.program_id)

    def run(self):
        asyncio.run(self.__conn.run())
