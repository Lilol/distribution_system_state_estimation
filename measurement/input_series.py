from logging import getLogger
from numbers import Number

from numpy import mean, isclose
from numpy import ndarray
from pandas import Series


class InputSeries:
    def __init__(self, data=None, uncertainty=None, count=None, std_dev=None, net=None, element=None, element_idx=None):
        if isinstance(data, Series):
            data = list(data)
        self.data = data
        self.uncertainty = uncertainty
        self.std_dev = std_dev
        self.net = net
        self.element = element
        self.idx = element_idx
        self._logger = getLogger("InputSeries")
        if isinstance(data, list) or isinstance(data, ndarray):
            # Check for one-element lists and one-element numpy arrays
            if (isinstance(data, list) and len(data) == 1) or \
                    (isinstance(data, ndarray) and data.ndim == 1 and data.shape[0] == 1) and count:
                self.data = data[0]
                self.count = count
            else:
                self.count = None
        elif isinstance(data, Number) and count:
            self.count = count
        elif net is None:
            raise ValueError("Count must be set for constant data series or network must be specified")

    def add_data(self, data):
        self.data = data

    def __iter__(self):
        if isinstance(self.data, list) or isinstance(self.data, ndarray):
            return SeriesIterator(self)
        elif self.net:
            return NetworkIterator(self)
        else:
            return ConstantIterator(self)

    def __getitem__(self, idx):
        if isinstance(self.data, list) or isinstance(self.data, ndarray):
            return self.data[idx]
        else:
            return self.data

    def get_std_dev(self):
        if self.std_dev is not None:
            if isclose(self.std_dev, 0., 1.e-19):
                self._logger.warning("std_dev too low, setting std dev to 0.001.")
                self.std_dev = 0.001
            return self.std_dev
        if self.uncertainty:
            return self.calculate_std_dev_from_uncertainty()
        else:
            raise RuntimeError("Either std_dev or uncertainty must be set!")

    def calculate_std_dev_from_uncertainty(self):
        self.std_dev = abs(mean(self.data) * self.uncertainty)
        if self.std_dev == 0.0:
            self._logger.warning("Measurement values too low, setting std dev to 0.001.")
            self.std_dev = 0.001
        return self.std_dev


class SeriesIterator:
    def __init__(self, series):
        self.__series = series
        self.__index = 0

    def __next__(self):
        index = self.__index
        self.__index += 1
        if index < len(self.__series.data):
            return self.__series.data[index]
        raise StopIteration


class ConstantIterator:
    def __init__(self, series):
        self.__series = series
        self.__index = 0

    def __next__(self):
        index = self.__index
        self.__index += 1
        if index < self.__series.count:
            return self.__series.data
        raise StopIteration


class NetworkIterator:
    def __init__(self, series):
        self.__net = series.net
        self.__el = series.element
        self.__idx = series.idx

    def __next__(self):
        if self.__el == "i":
            return self.__net.res_line.i_ka[self.__idx]
        elif self.__el == "v":
            return self.__net.res_bus.vm_pu[self.__idx]
        elif self.__el == "p":
            return self.__net.res_bus.p_mw[self.__idx]
        elif self.__el == "q":
            return self.__net.res_bus.q_mvar[self.__idx]
        else:
            raise StopIteration
