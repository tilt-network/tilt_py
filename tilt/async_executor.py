import asyncio
import threading


class AsyncExecutor:
    """
    Manages a background thread running an asyncio event loop.

    This allows synchronous code to execute asynchronous coroutines without
    blocking the main thread's flow or requiring the user to manage loops.
    """

    def __init__(self):
        """Initializes the event loop and starts it in a background daemon thread."""
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )
        self._thread.start()

    def _run_loop(self):
        """The entry point for the background thread; keeps the event loop running forever."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro):
        """
        Executes a coroutine in the background loop and waits for the result.

        Args:
            coro: The coroutine to execute.

        Returns:
            The result of the coroutine execution.
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def close(self):
        """
        Safely stops the background event loop and joins the thread.
        Ensures all pending tasks are handled before shutdown.
        """
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread.is_alive() and threading.current_thread() != self._thread:
            self._thread.join(timeout=2)
