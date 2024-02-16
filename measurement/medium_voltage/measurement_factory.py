from numpy import sum

from measurement.measurement_factory import MeasurementFactory
from measurement.measurement_store import MeasurementStore
from measurement.medium_voltage.measurement_preprocessor import MediumVoltageMeasurementPreprocessor, InputSource
from measurement.utility import NoMeasurementError
from utility.utils import get_number_of_slots_per_week


class MediumVoltageMeasurementFactory(MeasurementFactory):
    def __init__(self):
        super(MediumVoltageMeasurementFactory, self).__init__()
        self._measurement_preprocessor = MediumVoltageMeasurementPreprocessor()

    def set_network(self, network_type, network):
        super(MediumVoltageMeasurementFactory, self).set_network(network_type, network)

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
                                                                    InputSource.ACTIVE_POWER_MEASUREMENT.value),
                    axis=1)
                data_q_mvar = sum(
                    self._measurement_preprocessor.get_measurements(close_loads, for_validation, self._steps,
                                                                    InputSource.REACTIVE_POWER_MEASUREMENT.value),
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
                                     data=1.0, count=get_number_of_slots_per_week(),
                                     std_dev=self._measurement_preprocessor.deviation[InputSource.EXT_GRID_VOLTAGE])

        return measurements
