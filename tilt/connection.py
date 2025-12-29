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
from tilt.entities.auth import SkSignInResponse
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
    unwrap,
)


def custom_json_serializer(obj):
    """Serializes an object to JSON string and logs the output."""
    json_str = json.dumps(obj, cls=CustomJSONEncoder)
    TiltLog.info(f"Sending JSON: {json_str}")
    return json_str


class Connection:
    """Handles HTTP connections and API interactions for the Tilt service."""

    def __init__(self, options: Options):
        """Initializes the Connection with the given options."""
        self.__options = options
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Gets or creates an aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(json_serialize=custom_json_serializer)
        return self._session

    async def _handle_response(
        self,
        resp: aiohttp.ClientResponse,
        expected_status: int = 200,
        context: str = "",
    ) -> Result[dict, Error]:
        """Handles HTTP response, checking status and parsing JSON."""
        if resp.status != expected_status:
            body = await resp.text()
            return Err(
                Error(f"{context} Invalid response status {resp.status}: {body}")
            )

        try:
            data = await resp.json()
            return Ok(data)
        except Exception as e:
            return Err(Error(f"{context} Failed to parse JSON: {e}"))

    async def _handle_parsed_response(
        self,
        resp: aiohttp.ClientResponse,
        expected_status: int,
        from_json_func,
        context: str,
    ) -> Result:
        """Handles response and parses it into an object using the provided function."""
        match await self._handle_response(resp, expected_status, context):
            case Ok(data):
                try:
                    res = from_json_func(data)
                    return Ok(res)
                except TypeError as e:
                    TiltLog.error(f"{context} Failed to parse response: {e}")
                    return Err(Error(f"{context} Invalid response format: {e}"))
            case Err(error):
                return Err(error)

    async def close(self) -> None:
        """Closes the aiohttp session if open."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Enters the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exits the async context manager, closing the session."""
        await self.close()

    async def upload_program(
        self,
        filepath: str,
        name: Option[str] = None,
        description: Option[str] = None,
    ):
        """Uploads a program file to the Tilt platform."""
        url = programs_endpoint(self.__options.base_url)
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
            match await self._handle_response(resp, 200, "(upload_program)"):
                case Ok(data):
                    return data
                case Err(error):
                    TiltLog.error(f"Upload program failed: {error.message}")
                    raise RuntimeError(error.message)

    async def create_job(
        self, name: Option[str] = None, status: str = "pending"
    ) -> Result[Job, Error]:
        """Creates a new job on the Tilt platform."""
        url = jobs_endpoint(self.__options.base_url)

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
            return await self._handle_parsed_response(
                resp, 201, Job.from_json, "(create_job)"
            )

    async def create_task(
        self, job_id: UUID, index: int, status: str = "pending"
    ) -> Result[Task, Error]:
        """Creates a new task within a job on the Tilt platform."""
        url = tasks_endpoint(self.__options.base_url)

        headers = {
            "Authorization": f"Bearer {unwrap(self.__options.auth_token)}",
            "Content-Type": "application/json",
        }

        payload = {"job_id": job_id, "segment_index": index, "status": status}

        session = await self._get_session()
        async with session.post(url, json=payload, headers=headers) as resp:
            return await self._handle_parsed_response(
                resp, 201, Task.from_json, "(create_task)"
            )

    async def run_task(self, task_id: UUID, data: bytes) -> Result[Task, Error]:
        """Runs a task with the provided data on the Tilt platform."""
        url = run_task_endpoint(self.__options.base_url)

        headers = {"Authorization": f"Bearer {unwrap(self.__options.auth_token)}"}

        form = aiohttp.FormData()
        form.add_field("task_id", str(task_id))
        form.add_field("data", data, filename="data.dat")

        session = await self._get_session()
        async with session.post(url, data=form, headers=headers) as resp:
            return await self._handle_parsed_response(
                resp, 200, Task.from_json, "(run_task)"
            )

    async def sk_sign_in(self, sk: str) -> Result[SkSignInResponse, Error]:
        """Authenticates using a secret key and returns the sign-in response."""
        url = sk_signing_endpoint(self.__options.base_url)

        headers = {"Content-Type": "application/json"}
        payload = {"secret_key": sk}

        session = await self._get_session()
        async with session.post(url, json=payload, headers=headers) as resp:
            return await self._handle_parsed_response(
                resp, 200, SkSignInResponse.from_json, "(sk_sign_in)"
            )
