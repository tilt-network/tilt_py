from tilt.options import Options
from tilt.connection import Connection
import asyncio


class Tilt:

    def __init__(self, options: Options):
        self.__options = options
        if self.__options.data_src is None or self.__options.program_id is None:
            raise ValueError("Both data_src and program_id must be provided either directly or through options")

        self.__conn = Connection(self.__options.data_src, self.__options.program_id)

    def run(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            asyncio.ensure_future(self.__conn.run())
        else:
            asyncio.run(self.__conn.run())
