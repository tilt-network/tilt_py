import asyncio
import queue
import threading
import time
import warnings
from typing import Optional

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

from tilt.connection import Connection
from tilt.console import ChunkSpeedColumn
from tilt.log import TiltLog
from tilt.options import Options
from tilt.processed_data import ProcessedData

console = Console(stderr=True)


def _is_jupyter():
    try:
        from IPython.core.getipython import get_ipython

        ipy = get_ipython()
        return ipy is not None and "IPKernelApp" in ipy.config
    except (ImportError, NameError, AttributeError):
        return False


if _is_jupyter():
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass

warnings.filterwarnings(
    "ignore",
    message='install "ipywidgets" for Jupyter support',
    category=UserWarning,
    module="rich.live",
)


class Tilt:
    def __init__(self, options: Options):
        self.__options = options
        self.__conn = Connection(self.__options)

        if self.__options.data_src is None or self.__options.program_id is None:
            raise ValueError(
                "Both data_src and program_id must be provided either directly or through options"
            )

        if self.__options.secret_key is None:
            raise ValueError(
                "Secret key must be provided either directly or through options"
            )

        response = self.sk_sign_in(self.__options.secret_key)
        self.__options.auth_token = response["token"]
        self.__options.organization_id = response["organization"]["id"]

        self.organization_id = self.__options.organization_id

    def upload_program(
        self,
        filepath: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        async def run():
            await self.__conn.upload_program(filepath, name, description)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run())
        else:
            loop.create_task(run())

    def create_job(self, name: Optional[str] = None, status: str = "pending") -> dict:
        async def run():
            return await self.__conn.create_job(name, status)

        return self._run_async_blocking(run)

    def create_task(self, job_id: str, index: int, status: str = "pending") -> dict:
        async def run():
            return await self.__conn.create_task(job_id, index, status)

        return self._run_async_blocking(run)

    def run_task(self, task_id, data) -> dict:
        async def run():
            return await self.__conn.run_task(task_id, data)

        return self._run_async_blocking(run)

    def sk_sign_in(self, sk: str) -> dict:
        async def run():
            return await self.__conn.sk_sign_in(sk)

        return self._run_async_blocking(run)

    def _run_async_blocking(self, coro):
        try:
            return asyncio.run(coro())
        except RuntimeError:
            q: queue.Queue = queue.Queue()

            def runner():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    res = loop.run_until_complete(coro())
                    loop.close()
                    q.put((True, res))
                except Exception as e:
                    q.put((False, e))

            t = threading.Thread(target=runner)
            t.start()
            success, payload = q.get()
            t.join()

            if success:
                return payload
            raise payload

    def poll(self, job_id: str, task_id: str, segment_index: int):
        limit = 20
        count = 0

        while count < limit:
            count += 1
            try:
                processed_data = ProcessedData(
                    self.organization_id,
                    job_id,
                    task_id,
                    auth_token=self.__options.auth_token,
                )
                return processed_data.download()
            except Exception:
                time.sleep(2)

        raise TimeoutError(f"Segment {segment_index} timeout")

    def _process_chunk(
        self,
        job_id: str,
        index: int,
        chunk: bytes,
        statuses: list[str],
    ) -> bytes:
        statuses[index] = "running"

        task_info = self.create_task(job_id, index)
        task_id = task_info["id"]

        self.run_task(task_id, chunk)
        result = self.poll(job_id, task_id, index)

        assert isinstance(result, bytes), f"expected bytes, received {type(result)}"

        statuses[index] = "finished"
        return result

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
    ) -> list[tuple[int, Optional[bytes]]]:
        data = self.__options.data_src.jsonl_to_bytes_list()
        job = self.create_job(job_name)
        job_id = job["id"]

        statuses = ["pending"] * len(data)
        results: list[tuple[int, Optional[bytes]]] = []

        work_queue: queue.Queue[tuple[int, bytes]] = queue.Queue()
        result_queue: queue.Queue[tuple[int, Optional[bytes]]] = queue.Queue()

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
                    result_queue.put((idx, res))
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
