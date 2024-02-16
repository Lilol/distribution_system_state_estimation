import logging

import pandas as pd
from numpy import intersect1d
from pandas import DataFrame, read_excel

import utility.configuration as configuration
from data_extractor.definitions import GeneratorType, DataKind, data_kind_to_quantity, \
    data_kind_to_conversion_multiplier, data_kind_to_element_3ph, data_kind_to_element
from data_extractor.derived_data import DerivedData
from measurement.definitions import SmartMeterScenario
from measurement.measurement_perturber import MeasurementPerturber
from measurement.pilot.metering_device_position import element_selector
from network.definitions import Network


def extractor_factory(simulation_generator, simulator_network, data_kinds):
    if simulation_generator == GeneratorType.ESTIMATION:
        return EstimationDataExtractor(simulator_network, data_kinds)
    elif simulation_generator == GeneratorType.LOADFLOW:
        return LoadflowDataExtractor(simulator_network, data_kinds)
    elif simulation_generator == GeneratorType.FILE:
        return FileDataExtractor(simulator_network, data_kinds)
    else:
        raise ValueError(f"Generator type {simulation_generator} is invalid")


def _get_param_name_by_phase(param_name, phase_name="a"):
    index = param_name.find("_")
    return f"{param_name[:index]}_{phase_name}{param_name[index:]}"


class DataExtractor:
    def __init__(self, net, data_kinds):
        super().__init__()
        self._net = net
        self._bus = pd.DataFrame()
        self._line = pd.DataFrame()
        self._trafo = pd.DataFrame()
        self._logger = logging.getLogger("output_writer.data_extractor")
        self._i = 0
        self._save_s_v_e = configuration.config.getboolean("output", "save_derived_data")
        self._data_kinds = data_kinds
        self._derived_data = DerivedData(data_kinds)

    def init_elements(self):
        self._i += 1

    def get_data(self, data_kind, **kwargs):
        data = self._get_element(data_kind)[data_kind_to_element[data_kind]] * \
               data_kind_to_conversion_multiplier[data_kind]
        return data

    def calculate_derived_data(self):
        if not self._save_s_v_e:
            return
        self._derived_data.increment()
        for data_kind in self._data_kinds:
            self._derived_data.calculate(data_kind, self.get_data(data_kind))

    def retrieve_derived_data(self, data_kind, operation):
        if not self._save_s_v_e:
            return pd.DataFrame()
        else:
            return self._derived_data.retrieve(data_kind, operation)

    def get_element_names(self, data_kind):
        if "node" in data_kind:
            return self._net.bus.name
        elif "line" in data_kind:
            return self._net.line.name
        elif "trafo" in data_kind:
            return self._net.trafo.name
        else:
            raise Exception(f"Unknown data kind: {data_kind}")

    def _get_element(self, data_kind):
        if "node" in data_kind:
            return self._bus
        elif "line" in data_kind:
            return self._line
        elif "trafo" in data_kind:
            return self._trafo
        else:
            raise Exception(f"Unknown data kind: {data_kind}")


class EstimationDataExtractor(DataExtractor):
    def __init__(self, net, data_kinds):
        super(EstimationDataExtractor, self).__init__(net, data_kinds)

    def init_elements(self):
        self._i += 1
        self._bus = self._net.res_bus_est
        self._line = self._net.res_line_est
        self._trafo = self._net.res_trafo_est


class LoadflowDataExtractor(DataExtractor):
    def __init__(self, net, data_kinds):
        super(LoadflowDataExtractor, self).__init__(net, data_kinds)
        self.__measurement_perturber = MeasurementPerturber()

    def init_elements(self):
        self._i += 1
        self._bus = self._net.res_bus
        self._line = self._net.res_line
        self._trafo = self._net.res_trafo

    def get_data(self, data_kind, **kwargs):
        data = super(LoadflowDataExtractor, self).get_data(data_kind, **kwargs)
        if configuration.config.get_network() in (
                Network.BESNICA, Network.BESNICA_REDUCED) and data_kind == "node_voltage_pu":
            # this is important to get comparable SE and load-flow Excels
            load_flow_pu_multiplicator = configuration.config.getfloat("physics", "transformer_voltage_increase_factor")
            data = data * load_flow_pu_multiplicator
        if configuration.config.get_network() == Network.PILOT \
                and not configuration.config.getboolean("scenario", "meter_positioning"):
            data = self.__measurement_perturber.perturb_measurement(data, data_kind)
        return data


class FileDataExtractor(DataExtractor):
    def __init__(self, net, data_kinds):
        super(FileDataExtractor, self).__init__(net, data_kinds)
        self.__input_frame = read_excel(configuration.config.get("paths", "validation_data"), sheet_name=0, index_col=0,
                                        header=0)
        self.__input_frame.columns = self.__input_frame.columns.str.split('_', expand=True)
        self._supported_data_types = (DataKind.NODE_VOLTAGE.value, DataKind.LINE_CURRENT.value)

    def init_elements(self):
        self._i += 1

    def get_data(self, data_kind, **kwargs):
        if data_kind not in self._supported_data_types or data_kind_to_quantity(
                data_kind) not in self.__input_frame.columns.get_level_values(1):
            return DataFrame()
        selected = self.__input_frame[self.__input_frame.columns[
            self.__input_frame.columns.get_level_values(1) == data_kind_to_quantity(data_kind)]]
        selected.columns = [self.rename_to_index(col) for col in selected.columns]
        return selected.iloc[self._i - 1] * data_kind_to_conversion_multiplier[data_kind]

    def rename_col(self, col):
        element, quantity, _ = col
        el, el_type = element_selector(element, quantity)
        return self._net[el_type].loc[el, "name"]

    def rename_to_index(self, col):
        element, quantity, _ = col
        el, _ = element_selector(element, quantity)
        return el

    def get_element_names(self, data_kind):
        if data_kind not in self._supported_data_types:
            return []
        elif "node" in data_kind:
            return [self.rename_col(col) for col in
                    self.__input_frame.columns[self.__input_frame.columns.get_level_values(1) == "V"]]
        elif "line" in data_kind:
            return [self.rename_col(col) for col in
                    self.__input_frame.columns[self.__input_frame.columns.get_level_values(1) == "I"]]
        elif "trafo" in data_kind:
            return []
        else:
            raise Exception(f"Unknown data kind: {data_kind}")


class AsymmetricDataExtractor(LoadflowDataExtractor):
    def __init__(self, net, data_kinds):
        super().__init__(net, data_kinds)

    def init_elements(self):
        self._i += 1
        self._bus = self._net.res_bus_3ph
        self._line = self._net.res_line_3ph
        self._trafo = self._net.res_trafo_3ph

    def get_data(self, data_kind, **kwargs):
        if not kwargs["phase"]:
            return super().get_data(data_kind)
        else:
            data = self._get_element(data_kind)[
                       _get_param_name_by_phase(data_kind_to_element_3ph[data_kind], kwargs["phase"])] * \
                   data_kind_to_conversion_multiplier[data_kind]
        return data


class DifferenceDataExtractor(DataExtractor):
    def __init__(self, data_kinds, validator_network, simulator_network):
        super().__init__(simulator_network, data_kinds)

        simulation_generator = configuration.config.get_generator("simulation")
        self.__simulation_extractor = extractor_factory(simulation_generator, simulator_network, data_kinds)

        validator_generator = configuration.config.get_generator("validator")
        self.__validation_extractor = extractor_factory(validator_generator, validator_network, data_kinds)

        self.__measurement_perturber = MeasurementPerturber()

    def init_elements(self):
        super(DifferenceDataExtractor, self).init_elements()
        self.__simulation_extractor.init_elements()
        self.__validation_extractor.init_elements()

    def get_element_names(self, data_kind):
        return self.__validation_extractor.get_element_names(data_kind)

    def get_data(self, data_kind, **kwargs):
        if data_kind == "measurements":
            self._logger.warning("DifferenceDataExtractor measurements are simulation network measurements.")
            data = self.__simulation_extractor.get_data(data_kind)
        else:
            sim_data = self.__simulation_extractor.get_data(data_kind)
            ref_data = self.__validation_extractor.get_data(data_kind)

            if configuration.config.get_network() == Network.PILOT \
                    and not configuration.config.getboolean("scenario", "meter_positioning") and not isinstance(
                configuration.config.get_scenario(), SmartMeterScenario):
                ref_data = self.__measurement_perturber.perturb_measurement(ref_data, data_kind)

            # Set to p.u. for voltage differences
            if len(sim_data.index) != len(ref_data.index) or sim_data.index != ref_data.index:
                intersecting_cols = intersect1d(sim_data.index, ref_data.index)
                sim_data = sim_data[intersecting_cols]
                ref_data = ref_data[intersecting_cols]

            denominator = ref_data
            if "voltage" in data_kind and not isinstance(configuration.config.get("scenario", "scenario"),
                                                         SmartMeterScenario):
                denominator = 1
            data = (sim_data - ref_data) / denominator
        return data
