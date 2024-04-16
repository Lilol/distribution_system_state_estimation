import utility.configuration as configuration
from algorithm.definitions import AlgorithmAim
from algorithm.estimator import Estimator
from algorithm.loadflow import Loadflow, ControlledLoadflow
from algorithm.no_algorithm import NoAlgorithm
from data_extractor.definitions import GeneratorType
from measurement.definitions import ControlledScenario
from network.definitions import NetworkId


def algorithm_factory(generator, network=None, measurement_factory=None, aim=AlgorithmAim.INVALID):
    if generator == GeneratorType.ESTIMATION:
        return Estimator(network, measurement_factory, aim)
    elif generator == GeneratorType.LOADFLOW:
        if type(configuration.config.get_scenario()) == ControlledScenario or configuration.config.get_network_id() == NetworkId.ID_220018 and configuration.config.getboolean(
                "network.medium_voltage", "use_controller"):
            return ControlledLoadflow(network, measurement_factory, aim)
        else:
            return Loadflow(network, measurement_factory, aim)
    elif generator == GeneratorType.FILE:
        return NoAlgorithm(network, measurement_factory, aim)
    else:
        raise ValueError(f"Unknown generator type: {generator}")
