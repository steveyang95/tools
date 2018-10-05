import time


class StopwatchLap:

    def __init__(self, start_time=time.time(), end_time=time.time()):
        """

        :param start_time:
        :param end_time:
        """
        self.start = start_time
        self.end = end_time

    def calculate_time_elapsed(self):
        return self.end - self.start

    def set_start(self, start_time):
        self.start = start_time

    def set_end(self, end_time):
        self.end = end_time


class Stopwatch:
    def __init__(self, name):
        self.name = name
        self.laps = []
        self.current_lap = 0
        self.next_new_lap = 0

    def calculate_average_time(self):
        total_time = 0
        for lap in self.laps:
            if lap.calculate_time_elapsed() >= 0:
                total_time += lap.calculate_time_elapsed()

        return total_time / float(len(self.laps)) if len(self.laps) > 0 else 0

    def start_lap(self):
        self.laps.append(StopwatchLap())
        self.laps[self.next_new_lap].set_start(time.time())
        self.next_new_lap += 1

    def stop_lap(self):
        if self.current_lap < len(self.laps):
            self.laps[self.current_lap].set_end(time.time())
            self.current_lap += 1


class Clock:
    """
    A clock that contains instances of StopwatchLap classes.
    """

    def __init__(self):
        """

        """
        self.initial_start = time.time()
        self.current_lap = False
        self.stopwatches = {}

    def start_stopwatch(self, stopwatch_name):
        """

        :param stopwatch_name:
        :return:
        """
        if stopwatch_name not in self.stopwatches:
            self.stopwatches[stopwatch_name] = Stopwatch(stopwatch_name)

        self.stopwatches[stopwatch_name].start_lap()

    def stop_stopwatch(self, stopwatch_name):
        self.stopwatches[stopwatch_name].stop_lap()

    def get_average_time_elapsed(self, stopwatch_name):
        return self.stopwatches[stopwatch_name].calculate_average_time()

    def get_stopwatch_keys(self):
        return self.stopwatches.keys()
