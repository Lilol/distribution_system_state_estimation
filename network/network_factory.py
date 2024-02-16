import logging
from os import makedirs
from os.path import join, exists

import pandapower as pp

import utility.configuration as configuration
from measurement.load_measurement_pairing import LoadMeasurementPairer
from network.besnica.besnica import create_network as create_besnica_network
from network.controlled.build import build_controlled
from network.definitions import Network
from network.medium_voltage.network import build as build_medium_voltage
from network.network_kind_string import get_network_kind_string
from network.pilot.build_pilot import preprocess_network


def get_network_path(network):
    if network == Network.PILOT:
        path = configuration.config.get("paths", "pilot_path")
        filename = f"{configuration.config.get('network', 'network_file')}_{get_network_kind_string()}.xlsx"
    elif network in (Network.BESNICA, Network.BESNICA_REDUCED):
        path = configuration.config.get("paths", "besnica_input_path")
        filename = configuration.config.get("input", "besnica_network_file",
                                            fallback="besnica_symmetrical.xlsx")
    elif network == Network.CONTROLLED:
        path = configuration.config.get("paths", "controlled_path")
        filename = "network.xlsx"
    elif network == Network.MEDIUM_VOLTAGE:
        path = configuration.config.get("paths", "network_path")
        filename = f"{configuration.config.get('network', 'network_file')}.xlsx"
    else:
        raise ValueError(f"Unknown network type {network.value}")
    return path, filename


def network_factory():
    """Creates and returns a network based on the value of the argument parameter 'network type'
    network_type can be:
    1.) Besnica: basic, reduced
    2.) Pilot networks
    3.) Networks for controller scenarios
    4.) Medium voltage network of Movar
    """
    logger = logging.getLogger("network_factory")
    network = configuration.config.get_network()
    path, file = get_network_path(network)
    network_file = join(path, file)
    lmp = LoadMeasurementPairer()
    if configuration.config.getboolean("input", "load_network_from_file"):
        if exists(join(path, file)):
            logger.info(f"Network is being loaded from file '{network_file}'")
            net = lmp.add_load_measurement_pairing_to_network(pp.from_excel(network_file))
            if configuration.config.getboolean("network.medium_voltage", "use_controller"):
                pp.control.DiscreteTapControl(net, 40, 0.985, 1.015, in_service=True,
                                              drop_same_existing_ctrl=True)

            return net
        else:
            logger.warning(
                f"Cannot load network from file '{join(path, file)}', file doesn't exist, "
                "fallback: building network from scratch.")

    if network == Network.PILOT:
        net = lmp.add_load_measurement_pairing_to_network(preprocess_network())
    elif network in (Network.BESNICA, Network.BESNICA_REDUCED):
        net = create_besnica_network(network)
    elif network == Network.CONTROLLED:
        net = build_controlled(configuration.config.get("input", "network_id"))
    elif network == Network.MEDIUM_VOLTAGE:
        net = build_medium_voltage()
    else:
        raise ValueError(f"Unknown network type '{network.value}'")
    net.name = network.value

    if configuration.config.getboolean("output", "save_network_as_excel"):
        makedirs(path, exist_ok=True)
        logger.info(f"Saving network into file '{network_file}'")
        pp.to_excel(net, network_file, include_results=False)
    return net
