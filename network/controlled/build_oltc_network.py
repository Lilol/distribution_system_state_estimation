from os.path import join, exists

from pandapower import from_excel, drop_elements_simple, create_transformer_from_parameters, control, fuse_buses, \
    create_continuous_elements_index

import utility.configuration as configuration
from utility.visualize import visualize_network


def build(merge=False):
    network_file = join(configuration.config.get("paths", "controlled_path"), "network.xlsx")
    if not exists(network_file):
        raise RuntimeError(f"File '{network_file}' doesn't exist")
    net = from_excel(network_file)

    drop_elements_simple(net, "trafo", 0)
    drop_elements_simple(net, "controller", 0)

    create_transformer_from_parameters(net=net, hv_bus=68, lv_bus=69, sn_mva=0.4, vn_hv_kv=22, vn_lv_kv=0.42,
                                       vkr_percent=0.0385, vk_percent=4, pfe_kw=0.57, i0_percent=0.1425,
                                       shift_degree=150, tap_side="lv", tap_neutral=0, tap_max=4, tap_min=-4,
                                       tap_step_percent=2.5, tap_pos=1, in_service=True, name="1842593", oltc=True)

    control.DiscreteTapControl(net, 0, 0.985, 1.015, in_service=True)

    if merge:
        buses_to_merge = ((66, (67, 5, 4, 58, 59, 47, 46, 43)),
                          (64, (65, 3, 2, 60, 61)),
                          (0, (1, 62, 63, 7, 6, 56, 57, 42)),
                          (45, (13, 11, 12, 21, 24)),
                          (9, (48, 15, 8, 10, 51)),
                          (61, (69, 43, 42, 16, 17, 37)),
                          (20, (36, 18)),
                          (41, (22,)),
                          (40, (14,)))

        for prev_bus, to_merge in buses_to_merge:
            for bus in to_merge:
                fuse_buses(net, bus, prev_bus)
                prev_bus = bus

    return net
