from enum import Enum
from os.path import join, exists

from pandas import read_excel, DataFrame

import utility.configuration as configuration
from algorithm.definitions import AlgorithmAim
from data_extractor.definitions import OutputMode
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from measurement.utility import NoMeasurementError
from output_writer.assemble_path import assemble_file


class InputSource(Enum):
    ACTIVE_POWER_MEASUREMENT = "P"
    REACTIVE_POWER_MEASUREMENT = "Q"
    EXT_GRID_VOLTAGE = "U_EXT_GRID"


class MediumVoltageMeasurementPreprocessor(PilotMeasurementPreprocessor):
    deviation = {
        InputSource.ACTIVE_POWER_MEASUREMENT: configuration.config.getfloat("network.medium_voltage", "p_deviation"),
        InputSource.REACTIVE_POWER_MEASUREMENT: configuration.config.getfloat("network.medium_voltage", "q_deviation"),
        InputSource.EXT_GRID_VOLTAGE: configuration.config.getfloat("network.medium_voltage", "u_deviation")
    }

    def __init__(self):
        super(MediumVoltageMeasurementPreprocessor, self).__init__()
        self.__path = configuration.config.get("paths", "measurement_path")
        self.__input_frame = DataFrame()

    def __read_frame(self, week_num, for_validation):
        input_frame = read_excel(
            assemble_file("AMR_data", mode=OutputMode.EXCEL,
                          appendages=False, base_path=configuration.config.get("paths",
                                                                               "measurement_path"),
                          reference=for_validation, input_output="input"), sheet_name=0,
                        index_col=0, engine="openpyxl")
        input_frame.columns = input_frame.columns.str.split('_', expand=True)
        return input_frame

    def _read_weekly_data(self, week_num, for_validation=False):
        input_frame = self.__read_frame(week_num, True)
        return input_frame

    def _read_full_data(self):
        raise RuntimeError("Method is unimplemented.")

    def get_measurements(self, names, for_validation=False, number_of_time_slots=None, meas_type="P"):
        week_idx = configuration.config.getint("scenario", "week_index", fallback=1)
        assert 1 <= week_idx <= 52, "Week index is out of bounds, must be between [1, 52]"
        if self._use_weekly_data and self._week != week_idx:
            self._input_data = self._read_weekly_data(week_idx)
            self._week = week_idx
        return self.__select_from_meas_table(names, for_validation, number_of_time_slots, meas_type).values

    def get_measurement_sources(self, names, for_validation, meas_type):
        return self.__select_from_meas_table(names=names, for_validation=for_validation, meas_type=meas_type).columns. \
            get_level_values(2)

    def __select_from_meas_table(self, names, for_validation=False, number_of_time_slots=None, meas_type="P"):
        assert meas_type == "P" or meas_type == "Q"
        super(MediumVoltageMeasurementPreprocessor, self).get_measurements(names, for_validation)

        row_indexer = self._input_data.iloc[0:number_of_time_slots].index if number_of_time_slots is not None else \
            self._input_data.index
        col_indexer = (self._input_data.columns.get_level_values(0).astype("int").isin(names)) & \
                      (self._input_data.columns.get_level_values(1) == meas_type)

        if not col_indexer.any():
            raise NoMeasurementError(f"No measurement exists for loads '{names}'")
        return self._input_data.loc[row_indexer, col_indexer]
