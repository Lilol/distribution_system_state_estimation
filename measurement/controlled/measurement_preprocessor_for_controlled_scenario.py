from enum import Enum
from os.path import join, exists

from numpy import sqrt
from pandas import read_excel

import utility.configuration as configuration
from measurement.definitions import ControlledScenario
from measurement.pilot.pilot_measurement_preprocessor import PilotMeasurementPreprocessor
from network.definitions import NetworkId


class InputSource(Enum):
    ACTIVE_POWER_MEASUREMENT = "P"
    REACTIVE_POWER_MEASUREMENT = "Q"
    EXT_GRID_VOLTAGE = "U_EXT_GRID"
    UNCONTROLLED_VOLTAGE = "U_UNCONTROLLED"
    CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT = "U_CONTROLLED_WITH_PSEUDO"
    CONTROLLED_VOLTAGE = "U_CONTROLLED"


class MeasurementPreprocessorForControlledScenario(PilotMeasurementPreprocessor):
    header = {
        InputSource.ACTIVE_POWER_MEASUREMENT: [0],
        InputSource.EXT_GRID_VOLTAGE: None,
        InputSource.UNCONTROLLED_VOLTAGE: None,
        InputSource.CONTROLLED_VOLTAGE: None,
        InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT: None
    }

    index_col = {
        InputSource.ACTIVE_POWER_MEASUREMENT: 0,
        InputSource.EXT_GRID_VOLTAGE: None,
        InputSource.UNCONTROLLED_VOLTAGE: None,
        InputSource.CONTROLLED_VOLTAGE: None,
        InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT: None
    }

    cols_to_read = {
        InputSource.ACTIVE_POWER_MEASUREMENT: None,
        InputSource.EXT_GRID_VOLTAGE: "A",
        InputSource.UNCONTROLLED_VOLTAGE: "A",
        InputSource.CONTROLLED_VOLTAGE: "A",
        InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT: "A"
    }
    controller_source = {
        ControlledScenario.SC_1_NON_CONTROLLED: InputSource.UNCONTROLLED_VOLTAGE,
        ControlledScenario.SC_2_CONTROLLED: InputSource.CONTROLLED_VOLTAGE,
        ControlledScenario.SC_3_CONTROLLED_WITH_PSEUDO_MEASUREMENTS:
            InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT
    }
    filename = {
        InputSource.ACTIVE_POWER_MEASUREMENT: "measurements.xlsx",
        InputSource.REACTIVE_POWER_MEASUREMENT: "measurements.xlsx",
        InputSource.EXT_GRID_VOLTAGE: "ext_grid.xlsx",
        InputSource.UNCONTROLLED_VOLTAGE: "uncontrolled.xlsx",
        InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT: "pszeudo.xlsx",
        InputSource.CONTROLLED_VOLTAGE: "controlled.xlsx"
    }

    deviation = {
        InputSource.ACTIVE_POWER_MEASUREMENT: 0.01,
        InputSource.REACTIVE_POWER_MEASUREMENT: 0.01,
        InputSource.EXT_GRID_VOLTAGE: 0.01,
        InputSource.UNCONTROLLED_VOLTAGE: 0.01,
        InputSource.CONTROLLED_VOLTAGE: 0.005,
        InputSource.CONTROLLED_VOLTAGE_WITH_PSEUDO_MEASUREMENT: 0.005
    }

    def __init__(self):
        super(MeasurementPreprocessorForControlledScenario, self).__init__()
        self.__path = configuration.config.get("paths", "measurement_path")
        self.__input_frame = dict()
        cosphi = configuration.config.getfloat("physics", "cosphi")
        self.__p_to_q_factor = sqrt(1 - cosphi ** 2) / cosphi

        controlled_sources = list(self.controller_source.values()) if configuration.config.multi_unit_run() \
            else (self.controller_source[configuration.config.get_scenario()],)
        for source in (InputSource.ACTIVE_POWER_MEASUREMENT, InputSource.EXT_GRID_VOLTAGE):
            self.__fill_frame(source)
        for source in controlled_sources:
            self.__fill_frame(source)

    def __fill_frame(self, source):
        filename = join(self.__path, str(configuration.config.get("input", "network_id").value),
                        MeasurementPreprocessorForControlledScenario.filename[source])
        if not exists(filename):
            self._logger.warning(f"File '{filename}' is missing.")
            return
        self.__input_frame[source] = self.__read_input_frame(filename, self.header[source], self.index_col[source],
                                                             self.cols_to_read[source])

    def get_measurements(self, names=None, for_validation=False, number_of_time_slots=None,
                         meas_type=InputSource.ACTIVE_POWER_MEASUREMENT, week=None, first_index_to_return=0):
        scale = 1.
        if meas_type == InputSource.REACTIVE_POWER_MEASUREMENT:
            meas_type = InputSource.ACTIVE_POWER_MEASUREMENT
            scale = self.__p_to_q_factor

        if meas_type == InputSource.ACTIVE_POWER_MEASUREMENT \
                and configuration.config.get_network_id() == NetworkId.ID_23427:
            scale *= 1.5

        frame = self.__input_frame[meas_type]
        if number_of_time_slots is not None:
            row_indexer = range(0, number_of_time_slots)
        else:
            row_indexer = frame.index
        if meas_type in (InputSource.ACTIVE_POWER_MEASUREMENT, InputSource.ACTIVE_POWER_MEASUREMENT):
            col_indexer = self.__input_frame[meas_type].columns.astype("int").isin(names.astype("int"))
        else:
            col_indexer = frame.columns
        return frame.iloc[row_indexer, col_indexer].values * scale

    @staticmethod
    def __read_input_frame(filename, header, index_col, cols_to_read):
        input_frame = read_excel(filename, engine='openpyxl', sheet_name=0, header=header, index_col=index_col,
                                 usecols=cols_to_read)
        return input_frame

    def get_measurement_sources(self, close_loads, for_validation, param):
        pass
