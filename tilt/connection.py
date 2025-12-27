import json
from pathlib import Path
from uuid import UUID

import aiohttp

from tilt.endpoints import (
    jobs_endpoint,
    programs_endpoint,
    run_task_endpoint,
    sk_signing_endpoint,
    tasks_endpoint,
)
from tilt.entities.job import Job
from tilt.entities.task import Task
from tilt.log import TiltLog
from tilt.options import Options
from tilt.types import (
    CustomJSONEncoder,
    Err,
    Error,
    Ok,
    Option,
    Result,
    SkSignInResponse,
    unwrap,
)


def custom_json_serializer(obj):
    json_str = json.dumps(obj, cls=CustomJSONEncoder)
    TiltLog.info(f"Sending JSON: {json_str}")
    return json_str


class Connection:
    def __init__(self, options: Options):
        self.__options = options
        self._session: aiohttp.ClientSession | None = None

    # async def _get_session(self) -> aiohttp.ClientSession:
    #     if self._session is None:
    #         self._session = aiohttp.ClientSession(
    #             json_serialize=custom_json_serializer
    #         )
    #     return self._session

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(json_serialize=custom_json_serializer)
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def upload_program(
        self,
        filepath: str,
        name: Option[str] = None,
        description: Option[str] = None,
    ):
        url = programs_endpoint()
        headers = {"Authorization": f"Bearer {unwrap(self.__options.auth_token)}"}

        file_data = Path(filepath).read_bytes()

        form = aiohttp.FormData()
        form.add_field(
            "program",
            file_data,
            filename=Path(filepath).name,
            content_type="application/octet-stream",
        )
        form.add_field("organization_id", self.__options.organization_id)
        form.add_field("name", name)
        form.add_field("description", description)

        session = await self._get_session()
        async with session.post(url, data=form, headers=headers) as resp:
            if resp.status != 200:
                TiltLog.error(f"Error. Response status: {resp.status}")
            response = await resp.json()
        return response

    async def create_job(
        self, name: Option[str] = None, status: str = "pending"
    ) -> Result[Job, Error]:
        url = jobs_endpoint()

        headers = {
            "Authorization": f"Bearer {unwrap(self.__options.auth_token)}",
            "Content-Type": "application/json",
        }

        payload = {
            "organization_id": self.__options.organization_id,
            "name": name,
            "status": status,
            "total_tokens": 0,
            "program_id": self.__options.program_id,
        }

        session = await self._get_session()
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 201:
                body = await resp.text()
                return Err(
                    Error(f"(create_job) Invalid response status {resp.status}: {body}")
                )

            response_dict = await resp.json()

        try:
            res = Job.from_json(response_dict)
            return Ok(res)
        except TypeError as e:
            TiltLog.error(f"(create_job) Failed to create Job from response: {e}")
            return Err(Error(f"(create_job) Invalid response format: {e}"))

    async def create_task(
        self, job_id: UUID, index: int, status: str = "pending"
    ) -> Result[Task, Error]:
        url = tasks_endpoint()

        headers = {
            "Authorization": f"Bearer {unwrap(self.__options.auth_token)}",
            "Content-Type": "application/json",
        }

        payload = {"job_id": job_id, "segment_index": index, "status": status}

        # print(f"json headers: {json.dumps(headers, cls=CustomJSONEncoder)}")
        # print(f"json payload: {json.dumps(payload, cls=CustomJSONEncoder)}")
        # print(f"(create_task) json response: {json.dumps(data, cls=CustomJSONEncoder)}")

        session = await self._get_session()
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 201:
                TiltLog.error(f"Error. Response status (create_task): {resp.status}")
                return Err(Error(f"Invalid response status: {resp.status}"))

            data = await resp.json()
            try:
                task = Task.from_json(data)
                return Ok(task)
            except TypeError as e:
                TiltLog.error(f"Failed to create Task from response: {e}")
                return Err(Error(f"Invalid response format: {e}"))

    async def run_task(self, task_id: UUID, data: bytes) -> Result[Task, Error]:
        url = run_task_endpoint()

        headers = {"Authorization": f"Bearer {unwrap(self.__options.auth_token)}"}

        form = aiohttp.FormData()
        form.add_field("task_id", str(task_id))
        form.add_field("data", data, filename="data.dat")

        session = await self._get_session()
        async with session.post(url, data=form, headers=headers) as resp:
            try:
                response_dict = await resp.json()
            except Exception as e:
                TiltLog.error(f"Failed to parse response JSON: {e}")
                return Err(Error("Failed to parse response JSON"))

            if resp.status >= 300:
                TiltLog.error(
                    f"Error. (run_task) Response status: {resp.status}. Response body: {response_dict}"
                )
                return Err(
                    Error(
                        f"Error. (run_task) Response status: {resp.status}. Response body: {response_dict}"
                    )
                )

            try:
                # print(f"json headers: {json.dumps(headers, cls=CustomJSONEncoder)}")
                # print(f"json payload: {json.dumps(payload, cls=CustomJSONEncoder)}")
                # print(f"(run_task) json response: {json.dumps(response_dict, cls=CustomJSONEncoder)}")
                res = Task.from_json(response_dict)
                return Ok(res)
            except TypeError as e:
                TiltLog.error(f"Failed to run task from response: {e}")
                return Err(Error(f"Invalid response format: {e}"))

    async def sk_sign_in(self, sk: str) -> Result[SkSignInResponse, Error]:
        url = sk_signing_endpoint()

        headers = {"Content-Type": "application/json"}
        payload = {"secret_key": sk}

        session = await self._get_session()
        async with session.post(url, json=payload, headers=headers) as resp:
            try:
                response_dict = await resp.json()
            except Exception as e:
                TiltLog.error(f"Failed to parse response JSON: {e}")
                return Err(Error(f"Failed to parse response JSON: {e}"))

            if resp.status != 200:
                TiltLog.error(
                    f"Error. Response status: {resp.status}. Response body: {response_dict}"
                )
                return Err(Error(f"Failed to authenticate with secret key: {sk}"))

            try:
                res = SkSignInResponse.from_json(response_dict)
                return Ok(res)
            except TypeError as e:
                TiltLog.error(f"Failed to create Task from response: {e}")
                return Err(Error(f"Invalid response format: {e}"))
