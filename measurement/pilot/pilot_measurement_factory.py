from math import sqrt

from numpy import zeros, power, isnan

import utility.configuration as configuration
from measurement.measurement_factory import MeasurementFactory


class PilotMeasurementFactory(MeasurementFactory):
    _cosphi = configuration.config.getfloat("physics", "cosphi")
    _p_to_q_factor = sqrt(1 - _cosphi * _cosphi) / _cosphi

    def __init__(self):
        super().__init__()
        self._pseudo_measurement_uncertainty = configuration.config.getfloat("uncertainty",
                                                                             "pseudo_measurement")  # about 3 percent
        self._virtual_measurement_uncertainty = configuration.config.getfloat("uncertainty", "virtual_measurement")
        self._measurement_preprocessor = None

    def set_network(self, network_type, network):
        super(PilotMeasurementFactory, self).set_network(network_type, network)
        if not configuration.config.getboolean("scenario", "meter_positioning") or configuration.config.get(
                "validation", "validation_source") != "file":
            return
        self._measurement_preprocessor.read_measurement_tables()

    def create_measurements(self, for_validation=False):
        raise NotImplementedError("Method is not implemented")

    @staticmethod
    def _sum_node_measurements(measurement_identifiers, residential_measurements, residential_meas_dev,
                               controlled_measurements=None, controlled_meas_dev=None, pv_measurement=None):
        shape = list(residential_measurements.values())[0].shape
        sigma_sum = 0
        consumption_sum = zeros(shape[0] if shape[1:] else 1)
        use_pv = configuration.config.getboolean("scenario", "metering_position_use_pv")
        for meas_id in measurement_identifiers:
            if meas_id.residential_time_series_identifier.valid():
                consumption_sum += residential_measurements[meas_id.residential_time_series_identifier.cluster_name] \
                    [:, meas_id.residential_time_series_identifier.series_idx]
                sigma_sum += power(residential_meas_dev, 2)
            if controlled_measurements is not None and meas_id.controlled_time_series_identifier.valid():
                consumption_sum += controlled_measurements[:, meas_id.controlled_time_series_identifier.series_idx]
                sigma_sum += power(controlled_meas_dev, 2)
            if use_pv and not isnan(meas_id.pv_power_kwp) and pv_measurement is not None:
                consumption_sum -= pv_measurement * meas_id.pv_power_kwp
        return consumption_sum, sqrt(sigma_sum)
