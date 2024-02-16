from logging import getLogger

from pandapower import create_sgen, diagnostic, create_switch


def add_loads_and_generators(net):
    exclude = net.ext_grid.bus.values.tolist() + net.trafo.hv_bus.values.tolist() + net.trafo.lv_bus.values.tolist()
    for i, bus in net.bus.iterrows():
        if i in exclude:
            continue
        if any(net.load.bus == i):
            create_sgen(net, i, p_mw=0, name=f"sgen_{bus['name']}")

    # create_sgen(net, net.trafo.hv_bus[0], p_mw=0, name=f"sgen_Trafo")
    # create_load(net, net.trafo.hv_bus[0], p_mw=0, name=f"load_Trafo")


def merge_lines_with_impedance_close_to_zero(net):
    res = diagnostic(net, report_style=None)
    if res["impedance_values_close_to_zero"]:
        getLogger("network").warning(
            f"Some impedance values are close to zero, replacing them "
            f"with switches.")
        switches = []
        for key in res["impedance_values_close_to_zero"][0]:
            implausible_idx = res["impedance_values_close_to_zero"][0][key]
            net[key].in_service.loc[implausible_idx] = False
            for idx in implausible_idx:
                to_bus = net[key].to_bus.at[idx]
                from_bus = net[key].from_bus.at[idx]
                if [from_bus, to_bus] not in switches and [to_bus, from_bus] not in switches:
                    if not net.switch[
                        (net.switch.et == 'b') & (((net.switch.element == from_bus) & (net.switch.bus == to_bus)) |
                                                  ((net.switch.element == to_bus) & (
                                                          net.switch.bus == from_bus)))].empty:
                        continue
                    switches.append([from_bus, to_bus])
                    create_switch(net, from_bus, to_bus, et="b")