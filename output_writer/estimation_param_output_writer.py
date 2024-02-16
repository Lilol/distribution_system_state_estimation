from logging import getLogger
from platform import processor

import pandas as pd
from psutil import virtual_memory

import utility.configuration as configuration
from output_writer.output_writer import OutputWriter
from utility.performance import PerformanceMeasurer


class EstimationParamOutputWriter(OutputWriter):
    def __init__(self, estimation_params):
        super().__init__()
        self._filename = configuration.config.get("output", "estimation_param_output_file")
        self._estimation_params = estimation_params
        self._timer = PerformanceMeasurer()
        self._logger = getLogger("output_writer.estimation_params")

    def initialize(self, multi_unit_run=False, **kwargs):
        super().initialize(multi_unit_run)
        self._timer.reset()

    def write_step(self):
        if self._iteration_idx == 0:
            self._write_headers()
            self._iteration_idx += 1
            bytes_in_gig = 1073741824.
            self._write_data_column("system", pd.DataFrame([processor(), virtual_memory().total / bytes_in_gig]),
                                    self._iteration_idx)

        self._write_data_column("estimation", self._estimation_params.to_data_frame(), self._iteration_idx,
                                float_format="%.7f")
        self._iteration_idx += 1

    def write_final(self):
        self._write_data_column("performance", pd.DataFrame([self._timer.get_duration()]), 1, float_format="%.0f")

    def _write_headers(self):
        self._write_data_column("system", pd.DataFrame(["CPU", "RAM (GB)"]), 0)
        self._write_data_column("estimation", self._estimation_params.names_to_data_frame(), 0)
        self._write_data_column("performance", pd.DataFrame(["Simulation time (s)"]), 0)
