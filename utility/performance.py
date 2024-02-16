from time import time

from numpy import mean


class PerformanceMeasurer:
    """Measures and stores time periods in a list. Also calculates the mean of the stored time periods.

    Attributes
    ----------
    __iteration_times : List holding the measured time periods
    __start : The start of the last period measurement

    Methods
    ------
    start() : Starts the measurement by storing the current time value in __start
    stop() : Stops the measurement and stored the time period in __iteration_performances
    get_average() : Returns the average of the values stored in __iteration_performances
    get_duration() : Returns the elapsed time since start()
    """

    def __init__(self):
        self.__iteration_times = list()
        self.__start = time()

    def start(self):
        self.__start = time()

    def stop(self):
        self.__iteration_times.append(time() - self.__start)

    def reset(self):
        self.__iteration_times = list()
        self.__start = time()

    def get_average(self):
        return mean(self.__iteration_times)

    def get_duration(self):
        return time() - self.__start
