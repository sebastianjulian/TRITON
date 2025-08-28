import time

class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.perf_counter()
        self.end_time = None

    def stop(self):
        self.end_time = time.perf_counter()

    def elapsed(self):
        if self.start_time is None:
            return None
        if self.end_time is None:
            # If the stopwatch is still running, calculate elapsed time up to now
            return time.perf_counter() - self.start_time
        return self.end_time - self.start_time
    
    def per_second(self, iterations):
        return iterations / self.elapsed()