from os import path

from pandas import read_excel

import utility.configuration as configuration


class BesnicaInputReader:
    def __init__(self):
        self.__path = configuration.config.get("paths", "besnica_input_path")
        self.__file = configuration.config.get("input", "besnica_input_file")

        # input frame
        input_file = path.join(self.__path, self.__file)
        self.input_frame_p_mw = read_excel(input_file, engine='openpyxl', sheet_name="P_kWh",
                                           header=[0]) * 4 / 1000
        self.input_frame_q_mvar = read_excel(input_file, engine='openpyxl', sheet_name="Q_kVarh",
                                             header=[0]) * 4 / 1000
        self.days = read_excel(input_file, engine='openpyxl', sheet_name="days")

    def get_q_measurements(self, names, number_of_days=None, number_of_time_slots=None):
        if number_of_days is not None:
            return self.input_frame_q_mvar[names][0:number_of_days * number_of_time_slots].values
        else:
            return self.input_frame_q_mvar[names].values

    def get_p_measurements(self, names, number_of_days=None, number_of_time_slots=None):
        if number_of_days is not None:
            return self.input_frame_p_mw[names][0:number_of_days * number_of_time_slots].values
        else:
            return self.input_frame_p_mw[names].values
