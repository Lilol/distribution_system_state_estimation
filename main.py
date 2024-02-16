import logging

import utility.configuration as configuration
import utility.logging
from data_extractor.definitions import DataKind
from measurement.definitions import SmartMeterScenario
from simulation import Simulation, SimulationWithValidation
from utility.utils import init_random, display_error_variance_by_pos_sm

logging.getLogger("pandapower.create").setLevel(logging.CRITICAL)  # Get rid of PP's messages


def __simulation_factory():
    validate = configuration.config.getboolean("validation", "on")
    return Simulation() if not validate else SimulationWithValidation()


def main():
    utility.logging.init_logger()
    utility.utils.init_random()
    # display_error_variance_by_pos_sm(DataKind.NODE_VOLTAGE, scenario=SmartMeterScenario.SC_1_NoMeas)
    __simulation_factory().run()


if __name__ == '__main__':
    main()
