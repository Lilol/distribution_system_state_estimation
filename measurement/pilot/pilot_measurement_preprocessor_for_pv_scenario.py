from pandas import read_excel

import utility.configuration as configuration
from algorithm.definitions import AlgorithmAim
from data_extractor.definitions import OutputMode
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from measurement.utility import NoMeasurementError
from output_writer.assemble_path import assemble_file


class PilotMeasurementPreprocessorForPvScenario(PilotMeasurementPreprocessor):
    def __init__(self):
        super(PilotMeasurementPreprocessorForPvScenario, self).__init__()
        self._loc = configuration.config.get_network_id()

    def __read_frame(self, week_num, for_validation):
        input_frame = read_excel(
            assemble_file(f"measurement_{week_num}", mode=OutputMode.EXCEL,
                          appendages=False, base_path=configuration.config.get("paths",
                                                                               "measurement_path"),
                          reference=for_validation, input_output="input"), sheet_name="Sheet1",
            index_col=0, engine="openpyxl")
        input_frame.columns = input_frame.columns.str.split('_', expand=True)
        return input_frame

    def _read_weekly_data(self, week_num, for_validation=False):
        input_frame = {AlgorithmAim.VALIDATION: self.__read_frame(week_num, True),
                       AlgorithmAim.MAIN_SIMULATION: self.__read_frame(week_num, False)}
        return input_frame

    def _read_full_data(self):
        raise RuntimeError("Method is unimplemented.")

    def get_measurements(self, names, for_validation=False, number_of_time_slots=None, meas_type="P", week=None,
                         first_index_to_return=0):
        if week is None:
            week = configuration.config.getint("scenario", "week_index", fallback=1)
        assert 1 <= week <= 52, "Week index is out of bounds, must be between [1, 52]"
        loc = configuration.config.get_network_id()
        if self._use_weekly_data and (self._week != week or self._loc != loc):
            self._input_data = self._read_weekly_data(week)
            self._week = week
            self._loc = loc
        return self.__select_from_meas_table(names, for_validation, meas_type, number_of_time_slots,
                                             first_index_to_return).values

    def get_measurement_sources(self, names, for_validation, meas_type, number_of_time_slots=0, first_index=0):
        return self.__select_from_meas_table(names, for_validation, meas_type, number_of_time_slots,
                                             first_index).columns. \
            get_level_values(2)

    def __select_from_meas_table(self, names, for_validation=False, meas_type="P", number_of_time_slots=None,
                                 first_index=0):
        assert meas_type == "P" or meas_type == "Q"
        super(PilotMeasurementPreprocessorForPvScenario, self).get_measurements(names, for_validation)
        algo = AlgorithmAim.VALIDATION if for_validation else AlgorithmAim.MAIN_SIMULATION

        row_indexer = self._input_data[algo].iloc[
                      first_index:first_index + number_of_time_slots].index if number_of_time_slots is not None else \
            self._input_data[algo].index
        col_indexer = (self._input_data[algo].columns.get_level_values(0).astype("int").isin(names)) & \
                      (self._input_data[algo].columns.get_level_values(1) == meas_type)

        if not col_indexer.any():
            raise NoMeasurementError(f"No measurement exist for loads '{names}'")
        return self._input_data[algo].loc[row_indexer, col_indexer]
