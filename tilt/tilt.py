from tilt.options import Options
from tilt.connection import Connection
import asyncio


class Tilt:

    def __init__(self, options: Options):
        self.__options = options
        if self.__options.data_src is None or self.__options.program_id is None:
            raise ValueError("Both data_src and program_id must be provided either directly or through options")

        self.__conn = Connection(self.__options)

    def upload_program(self, filepath: str, name: str = None, description: str = None):
        async def run():
            await self.__conn.upload_program(filepath, name, description)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run())
        else:
            loop.create_task(run())

    def create_job(self, name: str = None, status: str = "pending"):
        async def run():
            return await self.__conn.create_job(name, status)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(run())
        else:
            return loop.run_until_complete(run())

    def create_task(self, job_id: str, index: int, status: str = "pending"):
        async def run():
            await self.__conn.create_task(job_id, index, status)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run())
        else:
            loop.create_task(run())
