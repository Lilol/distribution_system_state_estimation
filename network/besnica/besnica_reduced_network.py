# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 13:09:19 2021

@author: Gergő
"""

from os.path import join

import pandapower as pp

import network.besnica.besnica_reduced_create_all_network as create_all_network
import utility.configuration as configuration
from network import besnica as besnica_rename_them_all


def create_besnica_reduced_network():
    path = configuration.config.get("paths", "besnica_input_path")
    if configuration.config.getboolean("input", "load_network_from_file"):
        net = pp.from_excel(join(path, "besnica_reduced.xlsx"))
        return net

    # empty net
    net = pp.create_empty_network()

    # define line types based on Tavvez_param.xlsx
    NAYY = {"r_ohm_per_km": 0.443, "x_ohm_per_km": 0.082, "c_nf_per_km": 0, "max_i_ka": 0.179, "r0_ohm_per_km": 0.886,
            "x0_ohm_per_km": 0.164, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAYY, name="NAYY", element="line")
    NAYBY = {"r_ohm_per_km": 0.086, "x_ohm_per_km": 0.086, "c_nf_per_km": 0, "max_i_ka": 0.129, "r0_ohm_per_km": 0.172,
             "x0_ohm_per_km": 0.172, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAYBY, name="NAYBY", element="line")
    NA2XY = {"r_ohm_per_km": 0.868, "x_ohm_per_km": 0.073, "c_nf_per_km": 0, "max_i_ka": 0.135, "r0_ohm_per_km": 1.736,
             "x0_ohm_per_km": 0.146, "c0_nf_per_km": 0}
    pp.create_std_type(net, NA2XY, name="NA2XY", element="line")
    N1XD9AR = {"r_ohm_per_km": 0.496, "x_ohm_per_km": 0.1, "c_nf_per_km": 0, "max_i_ka": 0.223, "r0_ohm_per_km": 0.992,
               "x0_ohm_per_km": 0.2, "c0_nf_per_km": 0}
    pp.create_std_type(net, N1XD9AR, name="N1XD9AR", element="line")
    N1XD4AR = {"r_ohm_per_km": 2.139, "x_ohm_per_km": 0.1, "c_nf_per_km": 0, "max_i_ka": 0.098, "r0_ohm_per_km": 4.278,
               "x0_ohm_per_km": 0.2, "c0_nf_per_km": 0}
    pp.create_std_type(net, N1XD4AR, name="N1XD4AR", element="line")
    NAY2Y = {"r_ohm_per_km": 0.206, "x_ohm_per_km": 0.08, "c_nf_per_km": 0, "max_i_ka": 0.275, "r0_ohm_per_km": 0.412,
             "x0_ohm_per_km": 0.16, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAY2Y, name="NAY2Y", element="line")

    # create buses (Bálint Matlab input) from_bus, to_bus, length, type, name
    # created with from_string_to_python_input.py (other folder)
    base_network = [[1, 11, 105, 'NAYBY', 'S01'],
                    [11, 111, 104.9, 'NAYBY', 'S02'],
                    [11, 12, 220.6, 'NAYBY', 'S03'],
                    [12, 121, 112, 'NAYBY', 'S04'],
                    [12, 122, 64.1, 'NAYBY', 'S05']]

    # create mid-buses (Excel) which line, where
    # created with from_string_to_python_input_for_mid.py
    mid_buses = [['S02', 40.5],
                 ['S02', 86.6],
                 ['S02', 104.9],
                 ['S03', 48.8],
                 ['S03', 96.8],
                 ['S03', 146.6],
                 ['S04', 66.3],
                 ['S04', 112],
                 ['S05', 64.1]]

    # create mid-buses loads cosumption type, power
    # created with from_string_to_python_input_for_mid.py
    consumptions = [[4, 17],
                    [4, 14],
                    [4, 14],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [1, 6],
                    [4, 14],
                    [3, 6]]

    # all network as dict: name: [from_bus, to_bus, length, type]
    # and the names of the buses that contain loads
    all_network_as_graph, buses_of_loads = create_all_network.create(base_network, mid_buses)

    dict_of_buses = {}  # this dict contains the names as keys and the pp bus objects as data
    for line in all_network_as_graph:
        dict_of_buses[str(all_network_as_graph[line][0])] = None
        dict_of_buses[str(all_network_as_graph[line][1])] = None
    for bus in dict_of_buses:
        dict_of_buses[bus] = pp.create_bus(net, vn_kv=0.4, name=bus)

    # create network feeder rx_max (float, NaN) - maximal R/X-ratio to calculate internal impedance of ext_grid for
    # short circuit calculations s_sc_max_mva (float, NaN) - maximal short circuit apparent power to calculate
    # internal impedance of ext_grid for short circuit calculations r0x0_max (float, NaN) - maximal R/X-ratio to
    # calculate Zero sequence internal impedance of ext_grid x0x_max (float, NaN) - maximal X0/X-ratio to calculate
    # Zero sequence internal impedance of ext_grid
    pp.create_ext_grid(net, bus=dict_of_buses['1'], vm_pu=1.00, name="net Connection", s_sc_max_mva=1000, rx_max=1,
                       r0x0_max=1, x0x_max=1.0)

    # create first load
    pp.create_load(net, bus=dict_of_buses['11'], p_mw=0.017 / 3, q_mvar=0, sn_mva=0.017, name='11', scaling=1.0,
                   index=None, in_service=True, type='wye')
    # create loads
    i = 0
    for loads_bus in buses_of_loads:
        b = dict_of_buses[loads_bus]
        loads_consumption = consumptions[i][1]
        avg = loads_consumption / 3  # BE CAREFUL!!!!! these are the max values, to get a converged flow, use for
        # example loads_consumption/3000
        pp.create_load(net, bus=b, p_mw=avg, q_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                       scaling=1.0, index=None, in_service=True, type='wye')
        i += 1

    # renam loads by MeterNo.
    net = besnica_rename_them_all.rename_loads(net)

    # create lines
    dict_of_lines = {}  # this dict contains the names as keys and the pp line objects as data
    for line in all_network_as_graph:
        act = all_network_as_graph[line]
        dict_of_lines[line] = pp.create_line(net, from_bus=dict_of_buses[str(act[0])],
                                             to_bus=dict_of_buses[str(act[1])], length_km=act[2] / 1000,
                                             std_type=act[3], name=line)

    return net


def create_besnica_reduced_asymmetric_network():
    # empty net
    net = pp.create_empty_network()

    # define line types based on Tavvez_param.xlsx
    NAYY = {"r_ohm_per_km": 0.443, "x_ohm_per_km": 0.082, "c_nf_per_km": 0, "max_i_ka": 0.179, "r0_ohm_per_km": 0.886,
            "x0_ohm_per_km": 0.164, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAYY, name="NAYY", element="line")
    NAYBY = {"r_ohm_per_km": 0.086, "x_ohm_per_km": 0.086, "c_nf_per_km": 0, "max_i_ka": 0.129, "r0_ohm_per_km": 0.172,
             "x0_ohm_per_km": 0.172, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAYBY, name="NAYBY", element="line")
    NA2XY = {"r_ohm_per_km": 0.868, "x_ohm_per_km": 0.073, "c_nf_per_km": 0, "max_i_ka": 0.135, "r0_ohm_per_km": 1.736,
             "x0_ohm_per_km": 0.146, "c0_nf_per_km": 0}
    pp.create_std_type(net, NA2XY, name="NA2XY", element="line")
    N1XD9AR = {"r_ohm_per_km": 0.496, "x_ohm_per_km": 0.1, "c_nf_per_km": 0, "max_i_ka": 0.223, "r0_ohm_per_km": 0.992,
               "x0_ohm_per_km": 0.2, "c0_nf_per_km": 0}
    pp.create_std_type(net, N1XD9AR, name="N1XD9AR", element="line")
    N1XD4AR = {"r_ohm_per_km": 2.139, "x_ohm_per_km": 0.1, "c_nf_per_km": 0, "max_i_ka": 0.098, "r0_ohm_per_km": 4.278,
               "x0_ohm_per_km": 0.2, "c0_nf_per_km": 0}
    pp.create_std_type(net, N1XD4AR, name="N1XD4AR", element="line")
    NAY2Y = {"r_ohm_per_km": 0.206, "x_ohm_per_km": 0.08, "c_nf_per_km": 0, "max_i_ka": 0.275, "r0_ohm_per_km": 0.412,
             "x0_ohm_per_km": 0.16, "c0_nf_per_km": 0}
    pp.create_std_type(net, NAY2Y, name="NAY2Y", element="line")

    # create buses (Bálint Matlab input) from_bus, to_bus, length, type, name
    # created with from_string_to_python_input.py (other folder)
    base_network = [[1, 11, 105, 'NAYBY', 'S01'],
                    [11, 111, 104.9, 'NAYBY', 'S02'],
                    [11, 12, 220.6, 'NAYBY', 'S03'],
                    [12, 121, 112, 'NAYBY', 'S04'],
                    [12, 122, 64.1, 'NAYBY', 'S05']]

    # create mid-buses (Excel) which line, where
    # created with from_string_to_python_input_for_mid.py
    mid_buses = [['S02', 40.5],
                 ['S02', 86.6],
                 ['S02', 104.9],
                 ['S03', 48.8],
                 ['S03', 96.8],
                 ['S03', 146.6],
                 ['S04', 66.3],
                 ['S04', 112],
                 ['S05', 64.1]]

    # create mid-buses loads cosumption type, power
    # created with from_string_to_python_input_for_mid.py
    consumptions = [[4, 17],
                    [4, 14],
                    [4, 14],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [1, 6],
                    [4, 14],
                    [3, 6]]

    # all network as dict: name: [from_bus, to_bus, length, type]
    # and the names of the buses that contain loads
    all_network_as_graph, buses_of_loads = create_all_network.create(base_network, mid_buses)

    dict_of_buses = {}  # this dict contains the names as keys and the pp bus objects as data
    for line in all_network_as_graph:
        dict_of_buses[str(all_network_as_graph[line][0])] = None
        dict_of_buses[str(all_network_as_graph[line][1])] = None
    for bus in dict_of_buses:
        dict_of_buses[bus] = pp.create_bus(net, vn_kv=0.4, name=bus)

    # create network feeder rx_max (float, NaN) - maximal R/X-ratio to calculate internal impedance of ext_grid for
    # short circuit calculations s_sc_max_mva (float, NaN) - maximal short circuit apparent power to calculate
    # internal impedance of ext_grid for short circuit calculations r0x0_max (float, NaN) - maximal R/X-ratio to
    # calculate Zero sequence internal impedance of ext_grid x0x_max (float, NaN) - maximal X0/X-ratio to calculate
    # Zero sequence internal impedance of ext_grid
    pp.create_ext_grid(net, bus=dict_of_buses['1'], vm_pu=1.00, name="net Connection", s_sc_max_mva=1000, rx_max=1,
                       r0x0_max=1, x0x_max=1.0)

    # create first load
    pp.create_asymmetric_load(net, bus=dict_of_buses['11'], p_a_mw=0.017 / 3, p_b_mw=0.017 / 3, p_c_mw=0.017 / 3,
                              q_a_mvar=0, q_b_mvar=0, q_c_mvar=0, sn_mva=0.017, name='11', scaling=1.0, index=None,
                              in_service=True, type='wye')
    # create loads
    i = 0
    for loads_bus in buses_of_loads:
        b = dict_of_buses[loads_bus]
        loads_consumption = consumptions[i][1]
        loads_phase = consumptions[i][0]
        if loads_phase == 4:  # 3 phase
            avg = loads_consumption / 3  # BE CAREFUL!!!!! these are the max values, to get a converged flow, use for
            # example loads_consumption/3000
            pp.create_asymmetric_load(net, bus=b, p_a_mw=avg / 1000, p_b_mw=avg / 1000, p_c_mw=avg / 1000, q_a_mvar=0,
                                      q_b_mvar=0, q_c_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                                      scaling=1.0, index=None, in_service=True, type='wye')
        elif loads_phase == 3:  # C phase
            pp.create_asymmetric_load(net, bus=b, p_a_mw=0, p_b_mw=0, p_c_mw=loads_consumption / 1000, q_a_mvar=0,
                                      q_b_mvar=0, q_c_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                                      scaling=1.0, index=None, in_service=True, type='wye')
        elif loads_phase == 2:  # B phase
            pp.create_asymmetric_load(net, bus=b, p_a_mw=0, p_b_mw=loads_consumption / 1000, p_c_mw=0, q_a_mvar=0,
                                      q_b_mvar=0, q_c_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                                      scaling=1.0, index=None, in_service=True, type='wye')
        elif loads_phase == 1:  # A phase
            pp.create_asymmetric_load(net, bus=b, p_a_mw=loads_consumption / 1000, p_b_mw=0, p_c_mw=0, q_a_mvar=0,
                                      q_b_mvar=0, q_c_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                                      scaling=1.0, index=None, in_service=True, type='wye')
        i += 1

    # renam loads by MeterNo.
    net = besnica_rename_them_all.rename_asymmetric_loads(net)

    # create lines
    dict_of_lines = {}  # this dict contains the names as keys and the pp line objects as data
    for line in all_network_as_graph:
        act = all_network_as_graph[line]
        dict_of_lines[line] = pp.create_line(net, from_bus=dict_of_buses[str(act[0])],
                                             to_bus=dict_of_buses[str(act[1])], length_km=act[2] / 1000,
                                             std_type=act[3], name=line)

    # adds the zero sequence parameters of the standard types to the net model
    pp.add_zero_impedance_parameters(net)
    return net
