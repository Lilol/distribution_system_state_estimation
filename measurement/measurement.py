from measurement import input_series as ips


class Measurement:
    def __init__(self, name, measurement_type, element_type, element_idx, side=None, data=None, uncertainty=None,
                 without_noise=None, count=None, std_dev=None, net=None):
        self.name = name
        self.type = measurement_type
        self.element_type = element_type
        self.element_idx = element_idx
        self.element_side = side
        self.__input_series = ips.InputSeries(data, uncertainty, count, std_dev, net, measurement_type, element_idx)
        self.__input_series_iterator = iter(self.__input_series)

        if without_noise:
            self.__without_noise = ips.InputSeries(without_noise, count=count)
            self.__without_noise_iterator = iter(self.__without_noise)

    def get_next_measurement(self):
        return next(self.__input_series_iterator)

    def get_measurement_value(self, idx):
        return self.__input_series[idx]

    def get_std_dev(self):
        return self.__input_series.get_std_dev()

    def noiseless_available(self):
        if hasattr(self, '__without_noise'):
            return True
        else:
            return False

    def get_noiseless_measurement_value(self):
        if self.noiseless_available():
            return next(self.__without_noise_iterator)
        else:
            return next(self.__input_series_iterator)
