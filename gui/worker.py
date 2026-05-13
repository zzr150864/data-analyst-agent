"""Background analysis worker thread with thread-safe message queue."""

import threading
import queue
import traceback
import time


class AnalysisWorker(threading.Thread):
    """Runs the data analysis orchestrator in a background thread."""

    def __init__(self, orchestrator_factory, task: str):
        """
        Args:
            orchestrator_factory: Callable that takes (on_progress) and returns an orchestrator.
            task: Full analysis task string.
        """
        super().__init__(daemon=True)
        self._factory = orchestrator_factory
        self.task = task
        self.queue: queue.Queue = queue.Queue()
        self._cancel = threading.Event()
        self._start_time = None

    def cancel(self):
        self._cancel.set()
        self.queue.put({"type": "log", "text": "Cancelled by user."})

    def is_cancelled(self) -> bool:
        return self._cancel.is_set()

    def _on_progress(self, stage: str, pct: int):
        """Progress callback from orchestrator."""
        if self._cancel.is_set():
            raise InterruptedError("Analysis cancelled")
        self.queue.put({"type": "log", "text": f"[{pct}%] {stage}"})
        self.queue.put({"type": "progress", "value": pct})

    def run(self):
        self._start_time = time.time()
        try:
            self.queue.put({"type": "log", "text": "Initializing agents..."})
            self.queue.put({"type": "progress", "value": 2})

            orchestrator = self._factory(self._on_progress)

            self.queue.put({"type": "log", "text": "Analysis pipeline starting..."})
            self.queue.put({"type": "progress", "value": 5})

            result = orchestrator.run(self.task)

            elapsed = time.time() - self._start_time
            self.queue.put({"type": "log", "text": f"Completed in {elapsed:.1f}s."})
            self.queue.put({"type": "progress", "value": 100})
            self.queue.put({"type": "complete", "result": result, "elapsed": elapsed})

        except InterruptedError:
            self.queue.put({"type": "log", "text": "Analysis cancelled."})
            self.queue.put({"type": "progress", "value": 0})
        except Exception as e:
            self.queue.put({"type": "log", "text": f"ERROR: {e}"})
            self.queue.put({"type": "error", "message": str(e),
                           "traceback": traceback.format_exc()})
