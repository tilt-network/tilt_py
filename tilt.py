from options import Options
from connection import Connection
import asyncio
from typing import Optional


class Tilt:

    def __init__(self, data_src: Optional[str] = None, program_id: Optional[str] = None, options: Optional[Options] = None):
        if options is not None:
            self.__options = options
        else:
            self.__options = Options(None, data_src, program_id)
        
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
