from logging import getLogger

import utility.configuration as configuration
from measurement.utility import Singleton


class PilotMeasurementPreprocessor(metaclass=Singleton):
    def __init__(self):
        self._use_weekly_data = configuration.config.getboolean("input", "use_weekly_measurement_files")
        self._week = None
        if self._use_weekly_data:
            try:
                self._input_data = self._read_weekly_data(1)
            except Exception:
                self._input_data = None
        else:
            self._input_data = self._read_full_data()
        self._logger = getLogger("pilot_measurement_preprocessor")
        self._validation_network = None

    def _read_weekly_data(self, week_num, for_validation=False):
        raise RuntimeError("Method is unimplemented.")

    def _read_full_data(self):
        raise RuntimeError("Method is unimplemented.")

    def get_measurements(self, names, for_validation=False, number_of_time_slots=None, meas_type="P", week=None,
                         first_index_to_return=0):
        if week is None:
            week = configuration.config.getint("scenario", "week_index", fallback=1)
        assert 1 <= week <= 26, "Week index is out of bounds, must be between [1, 26]"
        if self._use_weekly_data and self._week != week:
            self._input_data = self._read_weekly_data(week, for_validation)
            self._week = week

    def set_validation_network(self, net):
        self._validation_network = net

    def get_validation_network(self):
        return self._validation_network
