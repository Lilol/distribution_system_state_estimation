from numpy import sum

import utility.configuration as configuration
from measurement.controlled.measurement_preprocessor_for_controlled_scenario import \
    MeasurementPreprocessorForControlledScenario, \
    InputSource
from measurement.definitions import ControlledScenario
from measurement.measurement_factory import MeasurementFactory
from measurement.measurement_store import MeasurementStore
from measurement.utility import NoMeasurementError


class ControlledScenarioMeasurementFactory(MeasurementFactory):
    __scen_to_meas = {
        ControlledScenario.SC_1_NON_CONTROLLED: InputSource.UNCONTROLLED_VOLTAGE,
        ControlledScenario.SC_2_CONTROLLED: InputSource.CONTROLLED_VOLTAGE,
        ControlledScenario.SC_3_CONTROLLED_WITH_PSEUDO_MEASUREMENTS:
            InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT
    }

    def __init__(self):
        super().__init__()
        self._measurement_preprocessor = MeasurementPreprocessorForControlledScenario()
        
    def set_network(self, network_type, network):
        super(ControlledScenarioMeasurementFactory, self).set_network(network_type, network)
        self._measurement_preprocessor.set_validation_network(network)

    def create_measurements(self, for_validation=False):
        measurements = MeasurementStore()
        load_bus = set()
        loads = self._net.load
        for _, R_load in loads.iterrows():
            # Aggregate loads that are at the same bus
            if R_load.bus in load_bus:
                continue

            load_bus.add(R_load.bus)
            close_loads = loads.name[loads.bus == R_load.bus]
            try:
                data_p_mw = sum(
                    self._measurement_preprocessor.get_measurements(close_loads, for_validation, self._steps,
                                                                    InputSource.ACTIVE_POWER_MEASUREMENT),
                    axis=1)
                data_q_mvar = sum(
                    self._measurement_preprocessor.get_measurements(close_loads, for_validation, self._steps,
                                                                    InputSource.REACTIVE_POWER_MEASUREMENT),
                    axis=1)

            except NoMeasurementError:
                continue

            measurements.add_measurement(name=f"{str(R_load['name'])}_P", measurement_type="p", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_p_mw,
                                         std_dev=self._measurement_preprocessor.deviation[
                                             InputSource.ACTIVE_POWER_MEASUREMENT])

            measurements.add_measurement(name=f"{str(R_load['name'])}_Q", measurement_type="q", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_q_mvar,
                                         std_dev=self._measurement_preprocessor.deviation[
                                             InputSource.REACTIVE_POWER_MEASUREMENT])

        measurements.add_measurement(name="V_ext_grid", measurement_type="v", element_type="bus",
                                     element_idx=self._net.ext_grid.bus[0],
                                     data=self._measurement_preprocessor.get_measurements(
                                         number_of_time_slots=self._steps,
                                         meas_type=InputSource.EXT_GRID_VOLTAGE),
                                     std_dev=self._measurement_preprocessor.deviation[InputSource.EXT_GRID_VOLTAGE])

        meas_type = self.__scen_to_meas[configuration.config.get_scenario()]
        controller_voltage = self._measurement_preprocessor.get_measurements(number_of_time_slots=self._steps,
                                                                             meas_type=meas_type).flatten()
        controlled_bus = self._net.controller.object[0].controlled_bus
        if not for_validation and configuration.config.get_scenario() == ControlledScenario.SC_2_CONTROLLED:
            measurements.add_measurement(name="V_controller", measurement_type="v", element_type="bus",
                                         element_idx=controlled_bus,
                                         net=self._measurement_preprocessor.get_validation_network(),
                                         std_dev=self._measurement_preprocessor.deviation[meas_type])
        else:
            measurements.add_measurement(name="V_controller", measurement_type="v", element_type="bus",
                                         element_idx=controlled_bus,
                                         data=controller_voltage,
                                         std_dev=self._measurement_preprocessor.deviation[meas_type])

        return measurements
