import utility.configuration as configuration
from network import network_factory
from network.definitions import NetworkId
from utility.utils import create_bus_bus_map


def func_to_stat(pilot):
    configuration.config.set("input", "network_id", str(pilot.value))
    print(f"Pilot ID: {pilot.value}")

    configuration.config.set_boolean("network", "cut_to_pieces", False)
    configuration.config.set_boolean("network", "build_exact", True)
    print("Building exact network.")
    net_exact = network_factory.network_factory()
    configuration.config.set_boolean("network", "cut_to_pieces", True)
    configuration.config.set_boolean("network", "build_exact", False)
    net_cut_to_pieces = network_factory.network_factory()
    create_bus_bus_map(net_exact, net_cut_to_pieces)


def stat_all():
    for network_id in (NetworkId.ID_20667,):
        configuration.config.set("input", "network_id", str(network_id.value))
        print(f"Pilot id {network_id}")
        for i in [1]:
            if i == 2:
                configuration.config.set_boolean("network", "cut_to_pieces", True)
                configuration.config.set_boolean("network", "build_exact", False)
                print("Cut to pieces.")
            elif i == 0:
                configuration.config.set_boolean("network", "cut_to_pieces", False)
                configuration.config.set_boolean("network", "build_exact", False)
                print("Closest.")
            elif i == 1:
                configuration.config.set_boolean("network", "cut_to_pieces", False)
                configuration.config.set_boolean("network", "build_exact", True)
                print("Exact.")

            func_to_stat()
