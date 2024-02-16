from os import makedirs
from os.path import join, exists

import utility.configuration as configuration
from data_extractor.definitions import OutputMode
from measurement.definitions import ControlledScenario, SmartMeterScenario
from network.network_kind_string import get_network_kind_string


def assemble_path(path=None, input_output=None, reference=False):
    multi_unit_run = configuration.config.multi_unit_run()
    pv_scenario_on = configuration.config.getboolean("multiple_run", "pv_scenario")
    if not path:
        path = configuration.config.get("paths", "output_path")
    if multi_unit_run:
        if pv_scenario_on:
            path = join(path, configuration.config.get_scenario().name, configuration.config.get_subscenario().name,
                        configuration.config.get_location_name())
            if input_output == "input":
                path = join(path, "reference" if reference else "data")
        elif type(configuration.config.get_scenario()) != ControlledScenario:
            path = join(path, get_network_kind_string())
    makedirs(path, exist_ok=True)
    return path


def assemble_file(filename, mode, appendages=True, base_path=None, reference=False, input_output=None):
    multi_unit_run = configuration.config.multi_unit_run()
    pv_scenario_on = configuration.config.getboolean("multiple_run", "pv_scenario")
    scenario = configuration.config.get_scenario()
    if multi_unit_run and not pv_scenario_on and not type(scenario) == ControlledScenario:
        metering_bus = f"_bus{str(configuration.config.getint('scenario', 'meter_positioning_bus'))}" if \
            configuration.config.getboolean("scenario", "meter_positioning") and appendages \
            else ""
        filename += f"_sc{str(configuration.config.get_scenario().value)}{metering_bus}"
    ext = ".xlsx" if mode == OutputMode.EXCEL else ".csv"

    if pv_scenario_on:
        return join(assemble_path(base_path, input_output, reference), filename + ext)

    return join(assemble_path(base_path), filename + ext)
