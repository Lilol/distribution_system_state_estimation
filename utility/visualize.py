from logging import getLogger
from os.path import join

import pandapower as pp
import pandapower.plotting.plotly as pplotly
from pandas import Series, DataFrame

import utility.configuration as configuration
from network import network_factory
from smart_meter_placement.accuracy_statistics import get_ordered_circuits
from smart_meter_placement.checkpoint_restart import get_fixed_meters
from utility.utils import create_bus_bus_map


# This file contains various function for visualizing networks and state estimation results.


def visualize_metering_points(pilot, metered=None, lines=None, draw_circuits_with_different_colors=False, other_metered=None,
                              add_pv=True, show_coordinate_network=True):
    # visualize_metering_points(PilotId.ID_18680, metered=[7, 16],
    #                           draw_circuits_with_different_colors=True, other_metered=[51], add_pv=True)
    # visualize_metering_points(PilotId.ID_20667, metered=[100, 33, 118, 59, 48, 69, 36, 9, 40],
    #                           draw_circuits_with_different_colors=True, other_metered=[151], add_pv=True)
    # visualize_metering_points(PilotId.ID_44600, metered=[88, 43, 11, 58, 39],
    #                           draw_circuits_with_different_colors=True, other_metered=[77], add_pv=True)
    # visualize_metering_points(PilotId.ID_44333, metered=[33, 53, 29, 11],
    #                           draw_circuits_with_different_colors=True, other_metered=[22], add_pv=True)
    """
    Visualizes a set of metering points.
    :param pilot: ID of the pilot location, can be: PilotId.ID_20667, PilotId.ID_44600, PilotId.ID_44333,
                  PilotId.ID_18680
    :param metered: Vector of metered bus indices, eg.: [10, 23, 12]
    :param draw_circuits_with_different_colors: Draws nodes that belong to the same circuit with a unified color.
                                                Circuit colors range from red to black.
    :param other_metered:  
    """
    configuration.config.set("input", "network_id", str(pilot.value))
    print(f"Pilot ID: {pilot.value}")
    print("Building cut to pieces network.")
    configuration.config.set_boolean("network", "cut_to_pieces", True)
    configuration.config.set_boolean("network", "build_exact", False)
    net = network_factory.network_factory()
    lines = [net.line[net.line.name.str.contains(l)].index[0] for l in lines]
    visualize_network(net, False, metered, filename_postfix="_schematic", highlight_lines=lines)

    print("Building exact network.")
    configuration.config.set_boolean("network", "cut_to_pieces", False)
    configuration.config.set_boolean("network", "build_exact", True)
    net2 = network_factory.network_factory()
    bus_map = create_bus_bus_map(net, net2)
    visualize_network(net2, False, [bus_map[m] for m in metered], filename_postfix="_coord", highlight_lines=lines)
    # circuits = get_ordered_circuits(net, no_checkpoint_restart=True) \
    #     if draw_circuits_with_different_colors or metered is None else None
    # if metered is None:
    #     metered = list(get_fixed_meters(len(circuits)).keys())



# Displays a network in the default renderer (browser).
def visualize_network(input_net, run_power_flow=False, highlight_buses=None, create_geocoordinates=False, circuits=None,
                      respect_switches=False, filename_postfix=None, highlight_lines=None):
    net = input_net.deepcopy()
    if run_power_flow:
        try:
            pp.runpp(net)
        except Exception:
            getLogger("visualization").warning("Loadflow did not converge, decreasing line loads with 90%")
            net.load.p_mw = net.load.p_mw / 10
            net.load.q_mvar = net.load.q_mvar / 10
            try:
                pp.runpp(net)
            except Exception:
                run_power_flow = False
                getLogger("visualization").warning("Loadflow did not converge after decreasing line loads with 90%, "
                                                   "setting 'run_power_flow' to False")

    if net.bus_geodata.empty or create_geocoordinates:
        if not net.bus_geodata.empty:
            net.bus_geodata.drop(net.bus_geodata.index, inplace=True)
        pp.plotting.create_generic_coordinates(net, respect_switches=respect_switches)
    else:
        if net.trafo.lv_bus[0] not in net.bus_geodata.index:
            net.bus_geodata = net.bus_geodata.append(DataFrame(net.bus_geodata.iloc[0], index=[net.trafo.lv_bus[0]]))
        if net.trafo.hv_bus[0] not in net.bus_geodata.index:
            net.bus_geodata = net.bus_geodata.append(DataFrame(net.bus_geodata.iloc[0], index=[net.trafo.hv_bus[0]]))

    if run_power_flow:
        bus_info = net.res_bus.vm_pu.astype(str) + " p.u."
        line_info = net.res_line.i_ka.astype(str) + " kA"
    else:
        if not net.res_bus_est.empty:
            bus_info = net.res_bus_est.vm_pu.astype(str) + " p.u."
            line_info = net.res_line_est.i_ka.astype(str) + " kA"
        elif not net.res_bus.empty:
            bus_info = net.res_bus.vm_pu.astype(str) + " p.u."
            line_info = net.res_line.i_ka.astype(str) + " kA"
        else:
            bus_info = net.bus.vn_kv.astype(str) + " kV"
            line_info = None

    # for _, sgen in net.sgen.iterrows():
    #     bus_info[sgen.bus] += f"<br>{sgen.p_mw * 1000} kW"

    if run_power_flow:
        if net.res_bus_est.empty and not net.res_bus.empty:
            cmap_vals = net.res_bus.vm_pu
            cmap_vals_i = net.res_line.i_ka
        else:
            cmap_vals = net.res_bus_est.vm_pu
            cmap_vals_i = net.res_line_est.i_ka
        cmap = True
    else:
        cmap = None
        cmap_vals = None
        cmap_vals_i = None

    bt = pplotly.create_bus_trace(net, buses=net.bus.index, cmap=cmap,
                                  cmap_vals=cmap_vals,
                                  infofunc=Series(index=net.bus.index, data=net.bus.name.astype(str) + '<br>' +
                                                                            net.bus.index.astype(str) + '<br>' +
                                                                            bus_info +
                                                                            '<br>'), cbar_title='Volt [pu]',
                                  size=7)

    if circuits is not None:
        for i, circuit in enumerate(circuits):
            bt += pplotly.create_bus_trace(net, buses=circuit.nodes,
                                           cbar_title=f"Circuit no. {str(i)}",
                                           size=10, color=f'rgba({i / len(circuits) * 254}, 0, 0, 1)')

    color_bar_position = 1.2
    lt = pplotly.create_line_trace(net, respect_switches=respect_switches, cmap=cmap, cmap_vals=cmap_vals_i, width=2,
                                   infofunc=Series(index=net.line.index,
                                                   data=net.line.name.astype(str) + '<br>' + ((line_info + '<br>') if
                                                                                              line_info is not None else "")),
                                   cbar_title='Current [A]', cpos=color_bar_position)

    new_lines = list()
    for j, switch in net.switch.iterrows():
        if switch.closed:
            if switch.et == "b":
                new_lines.append(pp.create_line(net, from_bus=switch.bus, to_bus=switch.element, length_km=0.01,
                                                std_type='NAYY 4x50 SE'))
            elif switch.et == "l":
                new_lines.append(pp.create_line(net, from_bus=switch.bus, to_bus=int(net.line.from_bus[switch.element]),
                                                length_km=0.01, std_type='NAYY 4x50 SE'))
    swt = pplotly.create_line_trace(net, lines=new_lines, color='grey')

    # st = pplotly.create_bus_trace(net, net.sgen.bus.values, patch_type="square", size=10, color="grey",
    #                               infofunc=Series(index=net.sgen.bus.values, data=net.sgen.name.astype(str) + '<br>' +
    #                                                                               net.sgen.p_mw.astype(str) + ' MW.' +
    #
    #                                                                               '<br>'))
    #
    # gt = pplotly.create_bus_trace(net, net.gen.bus.values, patch_type="square", size=8, color="black",
    #                               infofunc=Series(index=net.gen.bus.values, data=net.gen.name.astype(str) + '<br>' +
    #                                                                              net.gen.p_mw.astype(str) + ' MW.' +
    #                                                                              '<br>'))

    # traces = lt + bt + st + swt + st + gt
    traces = lt + bt + swt
    if not net.trafo.empty:
        traces += pplotly.create_trafo_trace(net, color="blue", width=2)

    if not net.trafo3w.empty:
        traces += pplotly.create_trafo_trace(net, color="green", trafotype="3W", width=3)

    # highlight_buses = list(net.load.bus)
    if highlight_buses is not None:
        mbt = pplotly.create_bus_trace(net, buses=highlight_buses, patch_type="diamond", color='pink', size=10)
        traces += mbt

    if highlight_lines is not None:
        hlt = pplotly.create_line_trace(net, lines=highlight_lines, width=2, color="pink")
        traces += hlt

    fig = pplotly.draw_traces(traces, showlegend=False, aspectratio=tuple([3, 3]))
    if configuration.config.getboolean("output", "save_vis_to_file"):
        fig.write_html(join(configuration.config.get("paths", "visualization_path"),
                            f"{configuration.config.get_location_name()}{filename_postfix}.html"))
