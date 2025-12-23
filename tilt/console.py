from rich.console import Console
from rich.progress import (
    ProgressColumn,
)
from rich.text import Text

console = Console(stderr=True)


class ChunkSpeedColumn(ProgressColumn):
    def render(self, task):
        if task.elapsed is None or task.elapsed == 0:
            return Text("?,?? chunk/s")

        speed = task.completed / task.elapsed
        return Text(f"{speed:.2f} chunk/s")
