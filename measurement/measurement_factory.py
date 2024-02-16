from numpy import mean

import utility.configuration as configuration
from utility.utils import get_number_of_slots_per_week


class MeasurementFactory:
    def __init__(self):
        self._network_name = None
        self._net = None
        self._steps = get_number_of_slots_per_week()
        self._zero_injection = configuration.config.getboolean("scenario", "zero_injection")
        self._input_reader = None
        self._measurement_preprocessor = None

    def set_network(self, network_type, network):
        self._network_name = network_type.value
        self._net = network
        if self._measurement_preprocessor:
            self._measurement_preprocessor.set_validation_network(network)

    def create_measurements(self, for_validation=False):
        raise NotImplementedError("Method not implemented")

    @staticmethod
    def _calculate_middle_point_of_measurement(measurements, default, min_measurement=1e-5):
        relevant_values = measurements[measurements > 0]
        middle = default
        if relevant_values.size:
            temp_mean = mean(relevant_values)
            middle = temp_mean if temp_mean > min_measurement else default
        return middle
