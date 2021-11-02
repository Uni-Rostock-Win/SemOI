import time
from typing import List


class PerformanceRegistry:
    """Stopwatch-Class that captures how fast the Calculation is performed
    """

    def __init__(self):
        self.entries = []

    def start(self, handle:str):
        """Starts the stopwatch for a task

        Args:
            handle (str): Task-Name

        Returns:
            PerformanceEntry: The PerformanceEntryCLass (self)
        """
        now = time.time()
        entry = PerformanceEntry(handle, now, self)
        self.entries.append(entry)
        return entry

    def relative(self)->List:
        """Returns the running times of all (stoped) entries

        Returns:
            List: stopped Entries
        """
        total = 0
        results = []
        for entry in self.entries:
            if entry.stopped is not None:
                total += entry.duration
        if total == 0:
            return results

        for entry in self.entries:
            if entry.stopped is not None:
                results.append([entry.handle, entry.duration, entry.duration / total])

        return results


class PerformanceEntry:
    """A running or stoped task-Stopwatch
    """
    def __init__(self, handle, started, registry):
        self.handle = handle
        self.started = started
        self.stopped = None
        self.registry = registry
        self.duration = None

    def stop(self):
        """Stops the Stopwatch of a PerformanceEntry
        """
        self.stopped = time.time()
        self.duration = self.stopped - self.started
