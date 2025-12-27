import asyncio
import atexit
import queue
import threading
import time
from uuid import UUID, uuid4

from rich.console import Console, Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.text import Text

from tilt.async_executor import AsyncExecutor
from tilt.connection import Connection
from tilt.console import ChunkSpeedColumn
from tilt.entities.auth import SkSignInResponse
from tilt.entities.job import Job
from tilt.entities.task import Task
from tilt.log import TiltLog
from tilt.options import Options
from tilt.processed_data import ProcessedData
from tilt.types import (
    Err,
    Error,
    Ok,
    Option,
    Result,
    Some,
    is_ok,
    is_some,
    unwrap_or,
)
from tilt.utils import _is_jupyter

console = Console(stderr=True)


class Tilt:
    """
    Main client for the Tilt API, providing tools for batch processing data
    using remote WASM programs.
    """

    def __init__(self, options: Options):
        """
        Initializes the Tilt client, performs authentication, and registers
        automatic cleanup handlers.

        Args:
            options: Configuration options including secret keys and data sources.

        Raises:
            ValueError: If mandatory credentials or program IDs are missing.
        """
        self._executor = AsyncExecutor()
        self.__options = options
        self.__conn = Connection(self.__options)

        atexit.register(self.close)

        if self.__options.data_src is None or self.__options.program_id is None:
            raise ValueError(
                "Both data_src and program_id must be provided either directly or through options"
            )

        match self.__options.secret_key:
            case Some(sk):
                result = self.sk_sign_in(sk)
            case None:
                raise ValueError(
                    "Secret key must be provided either directly or through options"
                )

        match result:
            case Ok(response):
                self.__options.auth_token = Some(response.token)
                self.__options.organization_id = response.organization.id
                self.organization_id = self.__options.organization_id

            case Err(value):
                print("Sign in error message:", value.message)

    def close(self):
        """
        Manual resource cleanup. Closes active network sessions and stops
        the background executor. Automatically called on script exit via atexit.
        """
        try:
            if self._executor._loop.is_running():
                self._run_async_blocking(self.__conn.close)
        except Exception:
            pass
        finally:
            self._executor.close()
            atexit.unregister(self.close)

    def upload_program(
        self,
        filepath: str,
        name: Option[str] = None,
        description: Option[str] = None,
    ):
        """
        Uploads a program (WASM) file to the Tilt platform.

        Args:
            filepath: Path to the local file.
            name: Optional display name for the program.
            description: Optional description of the program's functionality.
        """

        async def run():
            await self.__conn.upload_program(filepath, name, description)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run())
        else:
            loop.create_task(run())

    def create_job(
        self, name: Option[str] = None, status: str = "pending"
    ) -> Result[Job, Error]:
        """
        Creates a new Job entity to group multiple processing tasks.

        Returns:
            A Result containing the created Job or an Error.
        """

        async def run():
            return await self.__conn.create_job(name, status)

        return self._run_async_blocking(run)

    def create_task(
        self, job_id: UUID, index: int, status: str = "pending"
    ) -> Result[Task, Error]:
        """
        Creates a specific task segment within a Job.

        Args:
            job_id: The UUID of the parent job.
            index: The segment index for this specific chunk of data.
        """

        async def run():
            return await self.__conn.create_task(job_id, index, status)

        return self._run_async_blocking(run)

    def run_task(self, task_id: UUID, data: bytes) -> Result[Task, Error]:
        """
        Triggers the execution of a task with the provided binary data.
        """

        async def run():
            return await self.__conn.run_task(task_id, data)

        return self._run_async_blocking(run)

    def sk_sign_in(self, sk: str) -> Result[SkSignInResponse, Error]:
        """
        Authenticates the client using a secret key.
        """

        async def run():
            return await self.__conn.sk_sign_in(sk)

        return self._run_async_blocking(run)

    def _run_async_blocking(self, coro):
        return self._executor.run(coro())

    def poll(self, job_id: UUID, task_id: UUID, segment_index: int):
        """
        Wait and retrieve the result of a processed task from storage.

        Uses a retry mechanism with a timeout.

        Returns:
            The processed data as bytes.

        Raises:
            TimeoutError: If the data is not available within the time limit.
        """

        limit = 20
        count = 0

        while count < limit:
            count += 1
            try:
                processed_data = ProcessedData(
                    unwrap_or(self.organization_id, uuid4()),
                    job_id,
                    task_id,
                    auth_token=unwrap_or(self.__options.auth_token, ""),
                )
                return processed_data.download()
            except Exception:
                time.sleep(2)

        raise TimeoutError(f"Segment {segment_index} timeout")

    def _process_chunk(
        self,
        job_id: UUID,
        index: int,
        chunk: bytes,
        statuses: list[str],
    ) -> Result[bytes, Error]:
        """
        Internal orchestrator for a single data chunk: creates the task,
        runs it, and polls for the result.
        """

        statuses[index] = "running"

        task_info_result = self.create_task(job_id, index)
        match task_info_result:
            case Ok(task_info):
                if is_some(task_info.id):
                    task_id = task_info.id.value
                else:
                    return Err(Error("(process_chunk) Task ID doesn't exist"))
            case Err(error):
                return Err(Error(f"(process_chunk) Failed to create task: {error}"))

        self.run_task(task_id, chunk)
        result = self.poll(job_id, task_id, index)

        assert isinstance(result, bytes), f"expected bytes, received {type(result)}"

        statuses[index] = "finished"
        return Ok(result)

    def _create_progress(self, total: int) -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold]Processing tasks:[/]"),
            BarColumn(bar_width=None),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("|"),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TextColumn("<"),
            TimeRemainingColumn(),
            ChunkSpeedColumn(),
            expand=True,
        )

    def _render_lines(self, statuses: list[str]) -> Text:
        width = console.size.width
        text = Text()

        for i, status in enumerate(statuses):
            label = f"Task {i:03d}"
            status_str = status.capitalize()

            color = {
                "pending": "yellow",
                "running": "blue",
                "finished": "green",
                "failed": "red",
            }.get(status, "white")

            dots_count = max(
                1,
                width - len(label) - len(status_str) - 4,
            )
            dots = "." * dots_count

            line = Text()
            line.append(label + " ", style="bold")
            line.append(dots + " ")
            line.append(status_str, style=color)

            text.append(line)
            text.append("\n")

        return text

    def create_and_poll(
        self, job_name: str = "", max_workers: int = 16
    ) -> list[tuple[int, Option[bytes]]]:
        """
        High-level batch processor. Splits data, manages a thread pool for parallel
        execution, and displays a real-time progress UI.

        Args:
            job_name: Name for the processing job.
            max_workers: Maximum number of concurrent worker threads.

        Returns:
            A sorted list of tuples containing (index, processed_data).
        """

        data = self.__options.data_src.jsonl_to_bytes_list()
        job_result = self.create_job(Some(job_name))
        match job_result:
            case Ok(job):
                job = job
            case Err(_err):
                raise

        match job.id:
            case Some(id):
                job_id = id
            case None:
                raise

        statuses = ["pending"] * len(data)
        results: list[tuple[int, Option[bytes]]] = []

        work_queue: queue.Queue[tuple[int, bytes]] = queue.Queue()
        result_queue: queue.Queue[tuple[int, Option[bytes]]] = queue.Queue()

        for idx, chunk in enumerate(data):
            work_queue.put((idx, chunk))

        def worker():
            while True:
                try:
                    idx, chunk = work_queue.get_nowait()
                except queue.Empty:
                    return

                try:
                    res = self._process_chunk(job_id, idx, chunk, statuses)
                    if is_ok(res):
                        val = res.value
                        result_queue.put((idx, Some(val)))
                    else:
                        result_queue.put((idx, None))
                except Exception as e:
                    TiltLog.error(f"Chunk {idx} failed: {e}")
                    statuses[idx] = "failed"
                    result_queue.put((idx, None))
                finally:
                    work_queue.task_done()

        threads: list[threading.Thread] = []

        progress = self._create_progress(total=len(data))
        progress_task = progress.add_task("processing", total=len(data))

        with Live(
            Group(
                self._render_lines(statuses),
                progress,
            ),
            console=console,
            refresh_per_second=10,
        ) as live:
            for _ in range(max_workers):
                t = threading.Thread(target=worker)
                t.start()
                threads.append(t)

            completed = 0
            total = len(data)

            while completed < total:
                try:
                    idx, res = result_queue.get(timeout=0.1)
                    results.append((idx, res))
                    completed += 1

                    progress.advance(progress_task, 1)

                except queue.Empty:
                    pass

                live.update(
                    Group(
                        self._render_lines(statuses),
                        progress,
                    )
                )

            if _is_jupyter():
                time.sleep(0.5)
                live.update(
                    Group(
                        self._render_lines(statuses),
                        progress,
                    )
                )
                console.print("[green]Processing complete![/green]")  # opcional

            for t in threads:
                t.join()

        return sorted(results, key=lambda x: x[0])
