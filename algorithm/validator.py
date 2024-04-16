from logging import getLogger
from os.path import exists

from pandas import read_excel, DataFrame

import utility.configuration as configuration
from algorithm.algorithm import Algorithm
from algorithm.algorithm_factory import algorithm_factory
from algorithm.definitions import AlgorithmAim
from data_extractor.definitions import GeneratorType
from data_extractor.definitions import OutputMode
from output_writer.assemble_path import assemble_file, assemble_path


def validator_factory(validator_type, generator, network=None, measurement_factory=None,
                      aim=AlgorithmAim.INVALID):
    if validator_type == "algorithm":
        return AlgorithmValidator(algorithm=algorithm_factory(generator, network, measurement_factory, aim))
    elif validator_type == "file":
        return FileValidator(net=network, generator=generator)


class Validator(Algorithm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AlgorithmValidator(Validator):
    def __init__(self, **kwargs):
        self.__algorithm = kwargs["algorithm"]
        super().__init__(aim=AlgorithmAim.VALIDATION)

    def initialize(self, net=None):
        self.__algorithm.initialize(net)

    def set_measurements(self):
        self.__algorithm.set_measurements()

    def get_measurements(self):
        return self.__algorithm.get_measurements()

    def step(self, idx=None):
        return self.__algorithm.step(idx)


class FileValidator(Validator):
    def __init__(self, **kwargs):
        self.__path = assemble_path()
        self.__filename = configuration.config.get("output", "validation_result_file")
        self.__measurements = None
        self.__net = kwargs["net"]
        self.__table_voltage_pu = DataFrame()
        self.__table_voltage_angle = DataFrame()
        self.__generator = kwargs["generator"]
        super().__init__(aim=AlgorithmAim.VALIDATION)

    def initialize(self, net=None):
        file = assemble_file(self.__filename, OutputMode.EXCEL, appendages=False,
                             base_path=configuration.config.get("validation",
                                                                "input_path"))
        if not exists(file):
            getLogger("validator").error(f"File not found '{file}'")
            raise FileNotFoundError
        self.__table_voltage_pu = read_excel(file, sheet_name="node_voltage_pu", index_col=0, engine='openpyxl')
        self.__table_voltage_angle = read_excel(file, sheet_name="node_voltage_angle_deg", index_col=0,
                                                engine='openpyxl')
        self.__net = net

    def set_measurements(self):
        pass

    def get_measurements(self):
        return self.__measurements

    def step(self, idx=None):
        if self.__generator == GeneratorType.LOADFLOW:
            self.__net.res_bus["vm_pu"] = self.__table_voltage_pu.loc[idx + 1, :]
            self.__net.res_bus["va_degree"] = self.__table_voltage_angle.loc[idx + 1, :]
        else:
            self.__net.res_bus_est["vm_pu"] = self.__table_voltage_pu.loc[idx + 1, :]
            self.__net.res_bus_est["va_degree"] = self.__table_voltage_angle.loc[idx + 1, :]
