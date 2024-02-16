from os.path import join

from pandas import read_excel

import utility.configuration as configuration
from measurement.date_handler.date_assigner import DateIntervalCalculator
from measurement.definitions import BasicScenario
from measurement.pilot.metering_device_position import get_meas_points_based_on_scenario
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from measurement.pilot.pilot_measurement_preprocessor_for_basic_scenario import \
    PilotMeasurementPreprocessorForBasicScenario
from measurement.utility import _concatenate


class PilotSmartMeterMeasurementPreprocessor(PilotMeasurementPreprocessor):
    def __init__(self):
        self._power_measurement_preprocessor = PilotMeasurementPreprocessorForBasicScenario(join(
            configuration.config.get("paths", "home_dir"), "Measurements", "Basic"), BasicScenario.SC_2m)
        super(PilotSmartMeterMeasurementPreprocessor, self).__init__()
        self._date_processor = DateIntervalCalculator(output_year=2023)

    def _read_weekly_data(self, week_num, for_validation=False):
        raise RuntimeError("Do not use weekly data with smart meter measurements!")

    def _read_full_data(self):
        self._power_measurement_preprocessor._read_full_data()
        input_frame = read_excel(configuration.config.get("paths", "validation_data"), index_col=0, header=0)
        input_frame.columns = input_frame.columns.str.split('_', expand=True)
        return input_frame

    def get_measurements(self, names, for_validation=False, number_of_time_slots=None, meas_type="P", week=None,
                         first_index_to_return=0):
        super(PilotSmartMeterMeasurementPreprocessor, self).get_measurements(names, for_validation,
                                                                             number_of_time_slots, meas_type)
        assert week is None, "No week data is available for SM measurements."
        if meas_type not in ("P", "Q"):
            return self.__get_sm_measurements(meas_type, number_of_time_slots)
        dates = self._input_data.index
        time_units = self._date_processor.get_time_units(dates)
        output = None
        for time_unit in time_units:
            output = _concatenate(output,
                                  self._power_measurement_preprocessor.get_measurements(names, for_validation,
                                                                                        time_unit.length,
                                                                                        meas_type, time_unit.week,
                                                                                        time_unit.start_quarter_hour))
        return output

    def __get_sm_measurements(self, meas_types, number_of_time_slots=None):
        df = self._input_data.iloc[0:number_of_time_slots,
             self._input_data.columns.get_level_values(1).isin(meas_types)]
        meas_points = get_meas_points_based_on_scenario()
        if meas_points is None:
            return df
        return df[df.columns[df.columns.get_level_values(0).isin(meas_points)]]
