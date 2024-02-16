from measurement.measurement import Measurement


class MeasurementStore:
    def __init__(self):
        self.measurements = dict()
        self.time_idx = 0

    def add_measurement(self, name, measurement_type, element_type, element_idx, side=None, data=None,
                        uncertainty=None, without_noise=None, count=None, std_dev=None, net=None):
        self.measurements[name] = Measurement(name=name, measurement_type=measurement_type, element_type=element_type,
                                              element_idx=element_idx, side=side, data=data,
                                              uncertainty=uncertainty, count=count, without_noise=without_noise,
                                              std_dev=std_dev, net=net)

    def get_measurement(self, name):
        return self.measurements[name]

    def measurement_exists(self, name):
        return name in self.measurements

    def __getitem__(self, name):
        return self.get_measurement(name)

    def __iter__(self):
        return MeasurementIterator(self)


class MeasurementIterator:
    def __init__(self, measurement_store):
        self.__iter = iter(measurement_store.measurements.values())

    def __next__(self):
        return next(self.__iter)
