import asyncio
import aiohttp
from pathlib import Path
from tilt.endpoints import programs_endpoint, jobs_endpoint, tasks_endpoint, sk_signing_endpoint, run_task_endpoint
from tilt.options import Options
from tilt.log import TiltLog
from typing import Optional


class Connection:
    def __init__(self, options: Options):
        self.__options = options

    async def upload_program(self, filepath: str, name: Optional[str] = None, description: Optional[str] = None):
        url = programs_endpoint()
        headers = {
            "Authorization": f"Bearer {self.__options.auth_token}"
        }

        file_data = Path(filepath).read_bytes()

        form = aiohttp.FormData()
        form.add_field("program", file_data,
                       filename=Path(filepath).name,
                       content_type="application/octet-stream")
        form.add_field("organization_id", self.__options.organization_id)
        form.add_field("name", name)
        form.add_field("description", description)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, data=form) as resp:
                if resp.status != 200:
                    TiltLog.error(f"Error. Response status: {resp.status}")
                response = await resp.json()
        return response

    async def create_job(self, name: Optional[str] = None, status: str = "pending"):
        url = jobs_endpoint()

        headers = {
            "Authorization": f"Bearer {self.__options.auth_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "organization_id": self.__options.organization_id,
            "name": name,
            "status": status,
            "total_tokens": 0,
            "program_id": self.__options.program_id
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 201:
                    TiltLog.error(f"Error. Response status: {resp.status}")
                response = await resp.json()
        return response

    async def create_task(self, job_id: str, index: int, status: str = "pending"):
        url = tasks_endpoint()

        headers = {
            "Authorization": f"Bearer {self.__options.auth_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "job_id": job_id,
            "segment_index": index,
            "status": status
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 201:
                    TiltLog.error(f"Error. Response status: {resp.status}")
                response = await resp.json()
        return response

    async def run_task(self, task_id: str, data: bytes) -> dict:
            url = run_task_endpoint()

            headers = {
                "Authorization": f"Bearer {self.__options.auth_token}"
            }

            form = aiohttp.FormData()
            form.add_field("task_id", task_id)
            form.add_field("data", data, filename="data.dat")

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, data=form) as resp:
                    try:
                        return resp
                    except Exception as e:
                        TiltLog.error(f"Failed to parse response JSON: {e}")
                        response = None

                    if resp.status != 200:
                        TiltLog.error(f"Error. Response status: {resp.status}. Response body: {response}")

                    # return response

    async def sk_sign_in(self, sk: str) -> dict:
        url = sk_signing_endpoint()

        headers = {
            "Authorization": f"Bearer {self.__options.auth_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "secret_key": sk
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as resp:
                try:
                    response = await resp.json()
                except Exception as e:
                    TiltLog.error(f"Failed to parse response JSON: {e}")
                    response = None

                if resp.status != 200:
                    TiltLog.error(f"Error. Response status: {resp.status}. Response body: {response}")

                return response
