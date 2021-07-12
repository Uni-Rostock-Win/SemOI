import time


class PerformanceRegistry:

    def __init__(self):
        self.entries = []

    def start(self, handle):
        now = time.time()
        entry = PerformanceEntry(handle, now, self)
        self.entries.append(entry)
        return entry

    def relative(self):
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

    def __init__(self, handle, started, registry):
        self.handle = handle
        self.started = started
        self.stopped = None
        self.registry = registry
        self.duration = None

    def stop(self):
        self.stopped = time.time()
        self.duration = self.stopped - self.started
