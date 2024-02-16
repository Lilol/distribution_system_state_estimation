import logging

import utility.configuration as configuration
from measurement.definitions import SmartMeterScenario, scenario_to_deviation_controlled, scenario_to_deviation, \
    BasicScenario
from measurement.measurement_store import MeasurementStore
from measurement.pilot.metering_device_position import get_measurement_types_based_on_scenario, element_selector
from measurement.pilot.pilot_measurement_factory import PilotMeasurementFactory
from measurement.pilot.pilot_measurement_preprocessor_for_smart_meter_scenario import \
    PilotSmartMeterMeasurementPreprocessor
from utility.utils import get_number_of_slots_per_week


class PilotMeasurementFactoryForSmartMeterMeasurements(PilotMeasurementFactory):
    def __init__(self):
        super().__init__()
        self._measurement_preprocessor = PilotSmartMeterMeasurementPreprocessor()
        self._smart_measurement_u = configuration.config.getfloat("uncertainty", "smart_meter_measurement")
        self._trafo_voltage = configuration.config.getfloat("physics", "transformer_voltage_increase_factor")

    def create_measurements(self, for_validation=False):
        measurements_residential, measurements_controlled, _ = self._measurement_preprocessor.get_measurements(
            for_validation)

        measurements = MeasurementStore()
        already_encountered_loads = set()  # For collecting buses that has already been encountered
        count = get_number_of_slots_per_week()
        logging.getLogger("measurements").info(f"Creating measurements for '{count}' time slots")

        for i, R_load in self._net.load.iterrows():
            # Aggregate loads that are at the same bus
            # Don't add the same bus twice
            if R_load.bus in already_encountered_loads:
                continue
            already_encountered_loads.add(R_load.bus)

            data_p_mw, sigma_mw = self._sum_node_measurements(
                self._net.load_measurement_pairing[self._net.load.name[self._net.load.bus == R_load.bus]],
                measurements_residential, scenario_to_deviation[BasicScenario.SC_2m], measurements_controlled,
                scenario_to_deviation_controlled[BasicScenario.SC_2m])

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

        self.__add_smart_metered_measurements(measurements, for_validation)
        if configuration.config.get_scenario() in (SmartMeterScenario.SC_1_NoMeas, SmartMeterScenario.SC_2_Current):
            bus_index = self._net.trafo.hv_bus.at[0]
            measurements.add_measurement(name="V_trafo", measurement_type="v", element_type="bus",
                                         element_idx=bus_index,
                                         data=self._trafo_voltage, uncertainty=self._virtual_measurement_uncertainty,
                                         count=count)

        return measurements

    def __add_smart_metered_measurements(self, measurement_store, for_validation):
        if configuration.config.get("scenario", "scenario") == SmartMeterScenario.SC_1_NoMeas or for_validation:
            return

        sm_measurements = self._measurement_preprocessor.get_measurements(False,
                                                                          meas_type=get_measurement_types_based_on_scenario())
        for col in sm_measurements.columns:
            measurement_point, measurement_type, _ = col
            element, element_type = element_selector(measurement_point, measurement_type)
            measurement_store.add_measurement(name=f"{measurement_type}_{measurement_point}",
                                              measurement_type=measurement_type.lower(),
                                              element_type=element_type,
                                              side="from" if measurement_type == "I" else None,
                                              element_idx=element,
                                              data=sm_measurements[col].values,
                                              uncertainty=self._smart_measurement_u if measurement_type == "I" else 0.01 / 3.)
