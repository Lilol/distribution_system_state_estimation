import logging

from numpy import zeros

import utility.configuration as configuration
from measurement.definitions import scenario_to_deviation, scenario_to_deviation_controlled, SmartMeterScenario
from measurement.measurement_store import MeasurementStore
from measurement.pilot.pilot_measurement_factory import PilotMeasurementFactory
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from measurement.pilot.pilot_measurement_preprocessor_for_basic_scenario import \
    PilotMeasurementPreprocessorForBasicScenario
from network.definitions import NetworkId
from smart_meter_placement.accuracy_statistics import accuracy_statistics
from smart_meter_placement.measurements import create_meter_placement_measurements
from utility.utils import get_number_of_slots_per_week


class PilotMeasurementFactoryForBasicScenarios(PilotMeasurementFactory):
    def __init__(self):
        super().__init__()
        self._measurement_preprocessor = PilotMeasurementPreprocessorForBasicScenario()

    def create_measurements(self, for_validation=False):
        sc = configuration.config.get("scenario", "scenario")
        measurements_residential, measurements_controlled, pv_meas \
            = self._measurement_preprocessor.get_measurements(for_validation)
        measurements = MeasurementStore()

        load_bus = set()  # For collecting buses that has already been encountered

        count = get_number_of_slots_per_week()

        logging.getLogger("measurements").info(f"Creating measurements for '{count}' time slots")

        shape = list(measurements_residential.values())[0].shape
        sum_p = zeros(shape[0] if shape[1:] else 1)

        no_go_nodes = accuracy_statistics.circuit_root_nodes() + [
            configuration.config.getint("scenario", "meter_positioning_bus")]
        if configuration.config.get("input", "network_id") == NetworkId.ID_20667:
            no_go_nodes = []
        for i, R_load in self._net.load.iterrows():
            # Aggregate loads that are at the same bus
            # Don't add the same bus twice
            if R_load.bus in load_bus:
                continue

            load_bus.add(R_load.bus)

            # Don't define P, Q measurements for nodes at the beginning of circuits and currently metered bus
            if configuration.config.getboolean("scenario", "meter_positioning") and (
                    not for_validation and R_load.bus in no_go_nodes):
                continue

            data_p_mw, sigma_mw = self._sum_node_measurements(
                self._net.load_measurement_pairing[self._net.load.name[self._net.load.bus == R_load.bus]],
                measurements_residential, scenario_to_deviation[sc], measurements_controlled,
                scenario_to_deviation_controlled[sc], pv_meas)

            sum_p = sum_p + data_p_mw

            measurements.add_measurement(name=f"{str(R_load['name'])}_P", measurement_type="p", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_p_mw,
                                         std_dev=sigma_mw,
                                         count=count)

            measurements.add_measurement(name=f"{str(R_load['name'])}_Q", measurement_type="q", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_p_mw * self._p_to_q_factor,
                                         std_dev=sigma_mw,
                                         count=count)

        if configuration.config.getboolean("scenario", "meter_positioning") and not for_validation:
            create_meter_placement_measurements(measurements, PilotMeasurementPreprocessor(), self._net)

        bus_index = self._net.trafo.hv_bus.at[0]
        measurements.add_measurement(name="V_trafo", measurement_type="v", element_type="bus",
                                     element_idx=bus_index,
                                     data=1, uncertainty=self._virtual_measurement_uncertainty, count=count)

        return measurements
