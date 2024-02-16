from numpy import add, sum, zeros

import utility.configuration as configuration
from measurement.besnica import besnica_input_reader as beir
from measurement.measurement_factory import MeasurementFactory
from measurement.measurement_store import MeasurementStore


class BesnicaMeasurementFactory(MeasurementFactory):
    def __init__(self):
        super().__init__()
        self._input_reader = beir.BesnicaInputReader()

    def create_measurements(self, for_validation=False):
        measurements = MeasurementStore()
        pseudo_measurement_uncertainty = configuration.config.getfloat("uncertainty",
                                                                       "pseudo_measurement")  # about 3 percent
        virtual_measurement_uncertainty = configuration.config.getfloat("uncertainty", "virtual_measurement")

        ids = []
        uncertainties = []
        if configuration.config.has_option("uncertainty", "manual_specification_ids") and \
                configuration.config.has_option("uncertainty", "manual_specification_ids"):
            ids = list(map(int, configuration.config.get("uncertainty", "manual_specification_ids")))
            uncertainties = list(
                map(float, configuration.config.get("uncertainty", "manual_specification_uncertainties")))

        if self.__input_reader is None:
            self.__input_reader = beir.BesnicaInputReader()
        number_of_days = configuration.config.getint("time", "number_of_days")
        number_of_time_slots = configuration.config.getint("time", "number_of_time_slots")

        load_bus = set()
        sum_p = zeros((1, 1))
        sum_q = zeros((1, 1))
        loads = self._net.asymmetric_load if configuration.config.getboolean("scenario",
                                                                             "asymmetric") else self._net.load
        for _, R_load in loads.iterrows():
            # Aggregate loads that are at the same bus
            # Don't add the same bus twice
            if R_load.bus in load_bus:
                continue

            load_bus.add(R_load.bus)

            close_loads = loads.name[loads.bus == R_load.bus]

            data_p_mw = sum(self.__input_reader.get_p_measurements(close_loads, number_of_days, number_of_time_slots),
                            axis=1)
            data_q_mvar = sum(self.__input_reader.get_q_measurements(close_loads, number_of_days, number_of_time_slots),
                              axis=1)

            sum_p = add(sum_p, -1 * data_p_mw)
            sum_q = add(sum_q, -1 * data_q_mvar)

            mean_p = self._calculate_middle_point_of_measurement(data_p_mw, default=0.0003, min_measurement=1e-5)
            u = uncertainties[ids == R_load['name']] if uncertainties else pseudo_measurement_uncertainty
            measurements.add_measurement(name=f"{str(R_load['name'])}_P", measurement_type="p", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_p_mw,
                                         std_dev=u * mean_p)

            mean_q = self._calculate_middle_point_of_measurement(data_q_mvar, default=0.0002, min_measurement=1e-5)
            measurements.add_measurement(name=f"{str(R_load['name'])}_Q", measurement_type="q", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_q_mvar,
                                         std_dev=u * mean_q)

        measurements.add_measurement(name="V_trafo", measurement_type="v", element_type="bus", element_idx=0,
                                     data=configuration.config.getfloat("physics",
                                                                        "transformer_voltage_increase_factor",
                                                                        fallback=1),
                                     count=self._steps, std_dev=virtual_measurement_uncertainty)

        return measurements
