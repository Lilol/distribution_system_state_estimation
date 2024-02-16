from enum import Enum

from numpy import zeros, sum, add, sqrt

from measurement.measurement_store import MeasurementStore
from measurement.pilot.pilot_measurement_factory import PilotMeasurementFactory
from measurement.pilot.pilot_measurement_preprocessor_for_pv_scenario import PilotMeasurementPreprocessorForPvScenario
from measurement.utility import NoMeasurementError


class MeasurementSource(Enum):
    HistoricalDataset = "HD"
    HistoricalDatasetControlled2mm = "CHD2mm"
    HistoricalDatasetControlled2m = "CHD2m"
    SmartMeter = "SM"
    PV_TMY = "TMY"
    PV_CS = "CS"
    PV_Profile = "Prof"
    Invalid = "Invalid"


measurement_source_to_deviation = \
    {"p": {
        MeasurementSource.HistoricalDataset: 1.245,
        MeasurementSource.HistoricalDatasetControlled2mm: 0.466,
        MeasurementSource.HistoricalDatasetControlled2m: 0.433,
        MeasurementSource.SmartMeter: 0.448,
        MeasurementSource.PV_TMY: 0.316,
        MeasurementSource.PV_CS: 0.966,
        MeasurementSource.PV_Profile: 0.358,
        MeasurementSource.Invalid: 0.001
    },
        "q": {
            MeasurementSource.HistoricalDataset: 0.252,
            MeasurementSource.HistoricalDatasetControlled2mm: 0.133,
            MeasurementSource.HistoricalDatasetControlled2m: 0.142,
            MeasurementSource.SmartMeter: 0.147,
            MeasurementSource.PV_TMY: 0.102,
            MeasurementSource.PV_CS: 0.224,
            MeasurementSource.PV_Profile: 0.113,
            MeasurementSource.Invalid: 0.001,
        }
    }


def deviation(measurement_source_str, meas_type):
    return measurement_source_to_deviation[meas_type][MeasurementSource(measurement_source_str)]


class PilotMeasurementFactoryForPvScenario(PilotMeasurementFactory):
    def __init__(self):
        super().__init__()
        self._measurement_preprocessor = PilotMeasurementPreprocessorForPvScenario()

    def create_measurements(self, for_validation=False):
        measurements = MeasurementStore()

        load_bus = set()
        sum_p = zeros((1, 1))
        sum_q = zeros((1, 1))
        loads = self._net.load
        for _, R_load in loads.iterrows():
            # Aggregate loads that are at the same bus
            if R_load.bus in load_bus:
                continue

            load_bus.add(R_load.bus)

            close_loads = loads.name[loads.bus == R_load.bus]

            try:
                data_p_mw = sum(
                    self._measurement_preprocessor.get_measurements(close_loads, for_validation, self._steps, "P"),
                    axis=1)
                data_q_mvar = sum(
                    self._measurement_preprocessor.get_measurements(close_loads, for_validation, self._steps, "Q"),
                    axis=1)
            except NoMeasurementError:
                continue

            sum_p = add(sum_p, -1 * data_p_mw)
            sum_q = add(sum_q, -1 * data_q_mvar)
            measurements.add_measurement(name=f"{str(R_load['name'])}_P", measurement_type="p", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_p_mw,
                                         std_dev=sqrt(
                                             sum(deviation(ms, "p") ** 2 for ms in self._measurement_preprocessor.
                                                 get_measurement_sources(close_loads, for_validation, "P"))))

            measurements.add_measurement(name=f"{str(R_load['name'])}_Q", measurement_type="q", element_type="bus",
                                         element_idx=R_load.bus,
                                         data=data_q_mvar,
                                         std_dev=sqrt(
                                             sum(deviation(ms, "q") ** 2 for ms in self._measurement_preprocessor.
                                                 get_measurement_sources(close_loads, for_validation, "Q"))))

        measurements.add_measurement(name="V_trafo", measurement_type="v", element_type="bus",
                                     element_idx=self._net.trafo.hv_bus[0],
                                     data=1, count=self._steps, std_dev=self._virtual_measurement_uncertainty)

        return measurements
