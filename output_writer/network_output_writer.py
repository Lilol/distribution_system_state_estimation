import logging

import utility.configuration as configuration
from data_extractor import data_extractor as de, definitions
from data_extractor.definitions import GeneratorType, operation_to_name
from data_extractor.derived_data import Operation
from network.definitions import Network
from output_writer.output_writer import OutputWriter
from smart_meter_placement import accuracy_statistics


class NetworkOutputWriter(OutputWriter):
    def __init__(self, net, data_type=GeneratorType.ESTIMATION, name="", **kwargs):
        super().__init__()
        self._output_type = data_type
        self._filename = f"{configuration.config.get('output', 'network_output_file')}_{name}"
        if configuration.config.has_option("output", "output_types"):
            self._data_kinds = configuration.config.get("output", "output_types")
        elif configuration.config.get_network() == Network.PILOT:
            self._data_kinds = [definitions.DataKind.NODE_VOLTAGE.value, definitions.DataKind.NODE_VOLTAGE_ANGLE.value]
        else:
            self._data_kinds = definitions.DataKind.value.list()
        self._data_extractor = self._data_extractor_factory(data_type, self._data_kinds, net=net, **kwargs)
        self._logger = logging.getLogger("output_writer.network")
        self._iteration_idx = 0

    def initialize(self, multi_unit_run=False, **kwargs):
        super(NetworkOutputWriter, self).initialize(multi_unit_run, **kwargs)
        self._data_extractor = self._data_extractor_factory(self._output_type, self._data_kinds,
                                                            **kwargs)

    def write_step(self):
        self._data_extractor.init_elements()

        if self._iteration_idx == 0:
            self._write_index_row()
            self._iteration_idx += 1

        for data_kind in self._data_kinds:
            self._write_data_kind(data_kind)

        self._iteration_idx += 1

    def calculate(self):
        self._data_extractor.calculate_derived_data()

    def _write_index_row(self):
        for data in self._data_kinds:
            self._write_data_row(data, self._data_extractor.get_element_names(data), self._iteration_idx,
                                 header=["Iteration"])

    def _write_data_kind(self, data_kind):
        self._write_data_row(data_kind, self._data_extractor.get_data(data_kind), self._iteration_idx,
                             header=[str(self._iteration_idx)],
                             float_format=definitions.data_kind_to_format[data_kind])

    def _data_extractor_factory(self, data_type, data_kinds, **kwargs):
        if self._output_type == GeneratorType.ESTIMATION:
            return de.EstimationDataExtractor(kwargs["net"], data_kinds)
        elif self._output_type == GeneratorType.LOADFLOW:
            return de.LoadflowDataExtractor(kwargs["net"], data_kinds)
        elif self._output_type == GeneratorType.FILE:
            return de.FileDataExtractor(kwargs["net"], data_kinds)
        else:
            self._logger.error(f"Erroneous output type '{self._output_type}'")


class AsymmetricNetworkOutputWriter(NetworkOutputWriter):
    __all_data_kinds = [definitions.DataKind.NODE_VOLTAGE, definitions.DataKind.NODE_VOLTAGE_ANGLE,
                        definitions.DataKind.NODE_ACTIVE_POWER, definitions.DataKind.NODE_REACTIVE_POWER,
                        definitions.DataKind.LINE_CURRENT, definitions.DataKind.LINE_TO_ACTIVE_POWER,
                        definitions.DataKind.LINE_TO_REACTIVE_POWER, definitions.DataKind.LINE_FROM_REACTIVE_POWER,
                        definitions.DataKind.LINE_FROM_ACTIVE_POWER, definitions.DataKind.LINE_LOADING,
                        definitions.DataKind.LINE_ACTIVE_POWER_LOSS, definitions.DataKind.LINE_REACTIVE_POWER_LOSS,
                        definitions.DataKind.TRAFO_ACTIVE_POWER_LOSS, definitions.DataKind.TRAFO_REACTIVE_POWER_LOSS,
                        definitions.DataKind.TRAFO_ACTIVE_POWER_MV, definitions.DataKind.TRAFO_REACTIVE_POWER_MV,
                        definitions.DataKind.TRAFO_ACTIVE_POWER_LV, definitions.DataKind.TRAFO_REACTIVE_POWER_LV,
                        definitions.DataKind.TRAFO_CURRENT_LV, definitions.DataKind.TRAFO_CURRENT_MV,
                        definitions.DataKind.TRAFO_LOADING, definitions.DataKind.MEASUREMENTS]

    def __init__(self, net, data_type, name="asymmetric"):
        NetworkOutputWriter.__init__(self, net, data_type, name)
        if not configuration.config.has_option("output", "output_types"):
            self._data_kinds = self.__all_data_kinds

    def _write_data_kind(self, data_kind):
        if self._output_type == GeneratorType.ESTIMATION or data_kind == "measurements":
            super()._write_data_kind(data_kind)
        else:
            self.__write_3_phase_column(data_kind)

    def _write_index_row(self):
        if self._output_type == GeneratorType.ESTIMATION:
            super()._write_index_row()
            return
        for data_kind in self._data_kinds:
            if data_kind == "measurements":
                self._write_data_row(data_kind, self._data_extractor.get_element_names(data_kind),
                                     self._iteration_idx, header=["Iteration"])
            else:
                for phase in ["a", "b", "c"]:
                    self._write_data_row(f"{data_kind}_{phase}", self._data_extractor.get_element_names(data_kind),
                                         self._iteration_idx, header=["Iteration"])

    def \
            _data_extractor_factory(self, data_type, data_kinds, **kwargs):
        if data_type == GeneratorType.ESTIMATION:
            return de.EstimationDataExtractor(kwargs["net"], data_kinds)
        elif data_type == GeneratorType.LOADFLOW:
            return de.AsymmetricDataExtractor(kwargs["net"], data_kinds)
        else:
            self._logger.error(f"Erroneous output type '{str(self._output_type)}'")

    def __write_3_phase_column(self, data_kind):
        for phase in ["a", "b", "c"]:
            self._write_data_row(f"{data_kind}_{phase}", self._data_extractor.get_data(data_kind, phase=phase),
                                 self._iteration_idx, float_format=definitions.data_kind_to_format[data_kind],
                                 header=[str(self._iteration_idx)])


class DifferenceNetworkOutputWriter(NetworkOutputWriter):
    def __init__(self, validator_network, simulator_network, name="difference"):
        super().__init__(simulator_network, GeneratorType.DIFFERENCE, name=name,
                         simulator_network=simulator_network,
                         validator_network=validator_network)

    def _data_extractor_factory(self, data_type, data_kinds, **kwargs):
        accuracy_statistics.data_extractor = de.DifferenceDataExtractor(data_kinds,
                                                                        validator_network=kwargs["validator_network"],
                                                                        simulator_network=kwargs["simulator_network"])
        return accuracy_statistics.data_extractor

    def write_final(self):
        for data_kind in self._data_kinds:
            statistics_format = "%.8f"
            for i, operation in enumerate(Operation):
                self._write_data_row(data_kind, self._data_extractor.retrieve_derived_data(data_kind, operation),
                                     self._iteration_idx + i,
                                     float_format=statistics_format, header=[operation_to_name[operation]])
