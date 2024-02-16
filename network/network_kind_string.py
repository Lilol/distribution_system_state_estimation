from measurement.definitions import ControlledScenario
from network.definitions import NetworkKind
from utility import configuration as configuration


def get_network_kind_string():
    if type(configuration.config.get_scenario()) == ControlledScenario:
        return ""
    return NetworkKind.EXACT.value if configuration.config.getboolean("network", "build_exact") else \
        (NetworkKind.CUT_TO_PIECES.value if configuration.config.getboolean("network", "cut_to_pieces")
         else NetworkKind.CLOSEST.value)
