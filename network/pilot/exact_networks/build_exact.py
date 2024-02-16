import utility.configuration as configuration
from network.definitions import NetworkId
from network.pilot.exact_networks import build_exact_18680 as build_18680, build_exact_44333 as build_44333, \
    build_exact_20667 as build_20667, build_exact_44600 as build_44600


def build_exact(path="."):
    network_id = configuration.config.get("input", "network_id")

    if network_id == NetworkId.ID_18680:
        return build_18680.create(path)
    elif network_id == NetworkId.ID_44333:
        return build_44333.create(path)
    elif network_id == NetworkId.ID_44600:
        return build_44600.create(path)
    elif network_id == NetworkId.ID_20667:
        return build_20667.create(path)
    else:
        raise ValueError(f"Invalid pilot id '{str(network_id)}'")
