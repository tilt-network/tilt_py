from tilt.options import Options
from tilt.connection import Connection
import asyncio
from typing import Optional
import queue
import threading
from tilt.processed_data import ProcessedData
import time


class Tilt:
    def __init__(self, options: Options):
        self.__options = options
        self.__conn = Connection(self.__options)
        if self.__options.data_src is None or self.__options.program_id is None:
            raise ValueError("Both data_src and program_id must be provided either directly or through options")

        if self.__options.secret_key is None:
            raise ValueError("Secret key must be provided either directly or through options")

        response = self.sk_sign_in(self.__options.secret_key)
        self.__options.auth_token = response['token']
        self.__options.organization_id = response['organization']['id']

        self.organization_id = self.__options.organization_id

    def upload_program(self, filepath: str, name: Optional[str] = None, description: Optional[str] = None):
        async def run():
            await self.__conn.upload_program(filepath, name, description)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run())
        else:
            loop.create_task(run())

    def create_job(self, name: Optional[str] = None, status: str = "pending") -> dict:
        async def run() -> dict:
            return await self.__conn.create_job(name, status)

        try:
            return asyncio.run(run())
        except RuntimeError:
            q: queue.Queue = queue.Queue()

            def _runner():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    res = new_loop.run_until_complete(run())
                    new_loop.close()
                    q.put((True, res))
                except Exception as e:
                    q.put((False, e))

            t = threading.Thread(target=_runner, daemon=True)
            t.start()

            success, payload = q.get()
            if success:
                return payload
            else:
                raise payload

    def create_task(self, job_id: str, index: int, status: str = "pending") -> dict:
        async def run() -> dict:
            return await self.__conn.create_task(job_id, index, status)

        try:
            return asyncio.run(run())
        except RuntimeError:
            q: queue.Queue = queue.Queue()

            def _runner():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    res = new_loop.run_until_complete(run())
                    new_loop.close()
                    q.put((True, res))
                except Exception as e:
                    q.put((False, e))

            t = threading.Thread(target=_runner, daemon=True)
            t.start()

            success, payload = q.get()
            if success:
                return payload
            else:
                raise payload

    def run_task(self, task_id, data) -> dict:
        async def run() -> dict:
            return await self.__conn.run_task(task_id, data)

        try:
            return asyncio.run(run())
        except RuntimeError:
            q: queue.Queue = queue.Queue()

            def _runner():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    res = new_loop.run_until_complete(run())
                    new_loop.close()
                    q.put((True, res))
                except Exception as e:
                    q.put((False, e))

            t = threading.Thread(target=_runner, daemon=True)
            t.start()

            success, payload = q.get()
            if success:
                return payload
            else:
                raise payload

    def sk_sign_in(self, sk: str) -> dict:
        async def run() -> dict:
            return await self.__conn.sk_sign_in(sk)

        try:
            return asyncio.run(run())
        except RuntimeError:
            q: queue.Queue = queue.Queue()

            def _runner():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    res = new_loop.run_until_complete(run())
                    new_loop.close()
                    q.put((True, res))
                except Exception as e:
                    q.put((False, e))

            t = threading.Thread(target=_runner, daemon=True)
            t.start()

            success, payload = q.get()
            if success:
                return payload
            else:
                raise payload

    def poll(self, job_id: str, task_id: str, segment_index: int):
        limit = 20
        count = 0

        while count < limit:
            count += 1
            try:
                processed_data = ProcessedData(self.organization_id, job_id, task_id, auth_token=self.__options.auth_token)
                response = processed_data.download()
                print(f"Segment {segment_index} succeeded")
                return response
            except:
                print(f"Segment {segment_index} not ready yet, retrying…")
                time.sleep(3)

    def create_and_poll(self, job_name: str = "") -> list[tuple[int, bytes]]:
        job = self.create_job(job_name)
        job_id = job['id']
        processed_data = []
        data = self.__options.data_src.jsonl_to_bytes_list()
        for index, chunk in enumerate(data):
            task = self.create_task(job_id, index)
            task_id = task['id']
            segment_index = task['segment_index']
            self.run_task(task_id, chunk)
            result = self.poll(job_id, task_id, segment_index)
            processed_data.append((segment_index, result))

        return sorted(processed_data, key=lambda x: x[0])
