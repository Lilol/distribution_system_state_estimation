from network.controlled.build_ivr_network import build as build_ivr
from network.controlled.build_oltc_network import build as build_oltc
from network.definitions import NetworkId


def build_controlled(network_id):
    if network_id == NetworkId.ID_23427:
        return build_oltc()
    elif network_id == NetworkId.ID_99999:
        return build_ivr()
    else:
        raise ValueError(f"Invalid network ID for controlled scenario '{network_id.value}'")
