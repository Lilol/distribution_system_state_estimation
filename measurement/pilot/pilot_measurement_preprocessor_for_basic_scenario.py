from os.path import join, exists

from pandas import DataFrame, read_excel
from scipy.io import loadmat

import utility.configuration as configuration
from data_extractor.definitions import OutputMode
from measurement.definitions import BasicScenario
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from measurement.utility import _expand_arrays_to_2_dims
from output_writer.assemble_path import assemble_file
from utility.utils import get_number_of_slots_per_week


class PilotMeasurementPreprocessorForBasicScenario(PilotMeasurementPreprocessor):
    __scenario_to_data_field = \
        {BasicScenario.SC_1: "sc_1",  # P=const.=P_avg (all P measurements are constant averages from the whole year)
         BasicScenario.SC_1m: "sc_1m",  # P=const. <-- Calculated based on standard
         BasicScenario.SC_2: "sc_2",  # P=const.=P_mef (load-by-load)
         BasicScenario.SC_2m: "sc_2m",  # P(t)=profile(t)*P_mef (load-by-load, non-constant)
         BasicScenario.SC_2mm: "sc_2mm",  # P from smart metered data
         BasicScenario.REFERENCE: "reference"}  # Reference data series

    def __init__(self, path=None, scenario=None):
        self.__path = path if path is not None else join(configuration.config.get("paths", "home_dir"), "Measurements",
                                                         "Basic")
        super(PilotMeasurementPreprocessorForBasicScenario, self).__init__()
        self.__voltage_measurement_table = DataFrame()
        self.__current_measurement_table = DataFrame()
        self.__pv_measurement_table = self.__read_pv_data() if \
            (configuration.config.getboolean("scenario", "metering_position_use_pv")
             and configuration.config.getboolean("scenario", "meter_positioning")) else DataFrame()
        self.__sc = scenario

    def _read_full_data(self):
        return loadmat(join(self.__path, "measurements.mat"), squeeze_me=False,
                       struct_as_record=False, simplify_cells=True)["data"]

    def get_measurements(self, names, for_validation=False, number_of_time_slots=None, meas_type="P", week=None,
                         first_index_to_return=0):
        """Processes the mat file, reads measurements
            Parameters
            ----------
            first_index_to_return: The index of the first measurement to return
            names: Measurement points to return measurements for
            week: Week to return the measurements for
            for_validation : bool
                If true, the measurement values for the validation ('reference') are returned, otherwise, the
                measurements for the specified scenario are returned.
            number_of_time_slots: int, Number of measurements to return
            meas_type: str, Type of measurement to return
        """
        scenario = BasicScenario.REFERENCE if for_validation else (
            self.__sc if self.__sc is not None else configuration.config.get("scenario", "scenario",
                                                                             fallback="2mm"))
        super(PilotMeasurementPreprocessorForBasicScenario, self).get_measurements(names, for_validation,
                                                                                   number_of_time_slots, meas_type,
                                                                                   week)
        sc = self.__scenario_to_data_field[scenario]
        indexer = range(first_index_to_return, first_index_to_return + number_of_time_slots)
        if self._use_weekly_data:
            return _expand_arrays_to_2_dims(self._input_data['residential'][sc], indexer), \
                _expand_arrays_to_2_dims(self._input_data['controlled'][sc], indexer), \
                self.get_pv_data(for_validation)
        else:
            return _expand_arrays_to_2_dims(self._input_data['week'][week - 1]['residential'][sc], indexer), \
                _expand_arrays_to_2_dims(self._input_data['week'][week - 1]['controlled'][sc], indexer), \
                self.get_pv_data(for_validation)

    def read_measurement_tables(self):
        file = assemble_file(configuration.config.get("output", "validation_result_file"), OutputMode.EXCEL,
                             appendages=False,
                             base_path=configuration.config.get("validation", "input_path"))
        if not exists(file):
            self._logger.error(f"File not found '{file}'")
            raise FileNotFoundError
        self.__voltage_measurement_table = read_excel(file, sheet_name="node_voltage_pu", index_col=0,
                                                      engine='openpyxl')
        self.__current_measurement_table = read_excel(file, sheet_name='line_current_a', index_col=0,
                                                      engine='openpyxl')

    def get_measurement_tables(self):
        week_index = configuration.config.getint("scenario", "week_index")
        slot_length = get_number_of_slots_per_week()
        week_length = 7 * 96
        time_indices = range((week_index - 1) * week_length + 1, (week_index - 1) * week_length + 1 + slot_length)
        return self.__voltage_measurement_table.loc[time_indices], self.__current_measurement_table.loc[time_indices]

    def get_pv_data(self, for_validation=False):
        if not configuration.config.getboolean("scenario", "metering_position_use_pv"):
            return None
        slot_length = get_number_of_slots_per_week()
        time_indices = range(0, slot_length)
        column = "reference" if for_validation else "estimated"
        return self.__pv_measurement_table.loc[time_indices, column]

    def _read_weekly_data(self, week_idx, for_validation=False):
        self._week = week_idx
        return \
            loadmat(join(self.__path, f"measurements_week_{self._week}.mat"), squeeze_me=False, struct_as_record=False,
                    simplify_cells=True)["week"]

    def __read_pv_data(self):
        file = join(configuration.config.get("paths", "home_dir"), "PV_pszeudo_1het.xlsx")
        if not exists(file):
            self._logger.error(f"File not found '{file}'")
            raise FileNotFoundError
        return read_excel(file, sheet_name="data", engine='openpyxl')

