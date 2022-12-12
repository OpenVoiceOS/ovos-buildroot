import time


class Stopwatch:
    """
        Simple time measuring class.
    """
    def __init__(self):
        self.timestamp = None
        self.time = None

    def start(self):
        """
            Start a time measurement
        """
        self.time = None
        self.timestamp = time.time()

    def lap(self):
        cur_time = time.time()
        start_time = self.timestamp
        self.timestamp = cur_time
        return cur_time - start_time

    @property
    def delta(self):
        if not self.timestamp:
            # stopped or not started
            return self.time or 0
        return time.time() - self.timestamp

    def stop(self):
        """
            Stop a running time measurement. returns the measured time
        """
        cur_time = time.time()
        start_time = self.timestamp or cur_time
        self.time = cur_time - start_time
        self.timestamp = None
        return self.time

    def __enter__(self):
        """
            Start stopwatch when entering with-block.
        """
        self.start()

    def __exit__(self, tpe, value, tb):
        """
            Stop stopwatch when exiting with-block.
        """
        self.stop()

    def __str__(self):
        cur_time = time.time()
        if self.timestamp:
            return str(self.time or cur_time - self.timestamp)
        else:
            return 'Not started'

