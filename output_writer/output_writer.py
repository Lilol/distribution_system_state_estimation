from enum import Enum, auto
from logging import getLogger
from os.path import join

from pandas import ExcelWriter, DataFrame

import utility.configuration as configuration
from data_extractor.definitions import default_format, OutputMode
from output_writer.assemble_path import assemble_path, assemble_file


class OutputWriterKind(Enum):
    SIMULATION = auto()
    VALIDATION = auto()
    DIFFERENCE = auto()
    ESTIMATION_PARAMS = auto()
    METER_PLACEMENT = auto()


class OutputWriter:
    def __init__(self):
        self._writer = None
        self._logger = getLogger("output_writer")
        self._filename = None
        self._output_path = None
        self._iteration_idx = 0
        mode = configuration.config.get("output", "file_type")
        if mode == "excel":
            self._mode = OutputMode.EXCEL
        elif mode == "csv":
            self._mode = OutputMode.CSV
        else:
            self._logger.warning(f"Unknown output file type '{mode}', using csv instead.")
            self._mode = OutputMode.CSV

    def initialize(self, multi_unit_run=False, **kwargs):
        self._output_path = assemble_path()
        output_file = assemble_file(self._filename, self._mode)

        self._logger.info(f"Initializing output file: '{output_file}'")
        if self._mode == OutputMode.EXCEL:
            self._writer = ExcelWriter(output_file, mode='w')
        self._iteration_idx = 0

    def write_step(self):
        pass

    def write_final(self):
        pass

    def save(self):
        if self._mode == OutputMode.EXCEL and self._writer:
            self._writer.save()

    def calculate(self):
        pass

    def _get_output_file(self, data_type):
        extension = ".xlsx" if self._mode == OutputMode.EXCEL else ".csv"
        output_file = join(self._output_path, f"{self._filename}_{data_type}{extension}")
        return output_file

    def _write_data_column(self, data_type, data, column, header=False, float_format=default_format):
        if len(data_type) > 31:
            data_type = data_type[:30]
        if self._mode == OutputMode.EXCEL:
            data.to_excel(self._writer, sheet_name=data_type, header=header, index=False, startcol=column,
                          float_format=float_format)

    def _write_data_row(self, data_type, data, row, header=False, float_format=default_format):
        if len(data_type) > 31:
            data_type = data_type[:30]
        if not header:
            label = str(row)
        else:
            label = header

        frame_to_write = DataFrame(data).T
        if header is not None:
            frame_to_write.index = label
        if self._mode == OutputMode.EXCEL:
            if header is None:
                frame_to_write.to_excel(self._writer, sheet_name=data_type, index=True, startrow=row,
                                        float_format=float_format, header=None)
            else:
                frame_to_write.to_excel(self._writer, sheet_name=data_type, index=True, startrow=row,
                                        float_format=float_format, header=False)
        elif self._mode == OutputMode.CSV:
            frame_to_write.to_csv(self._get_output_file(data_type), mode='a', index=True, header=False,
                                  float_format=float_format)
