# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 12:36:42 2021

@author: Gergő
"""
import pandapower as pp

import network.besnica.besnica_create_all_network as create_all_network
import network.besnica.besnica_rename_them_all


def create_besnica_symmetrical_network():
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
                    [12, 122, 64.1, 'NAYBY', 'S05'],
                    [1, 21, 172.5, 'NAY2Y', 'S06'],
                    [1, 31, 42.5, 'N1XD9AR', 'S07'],
                    [31, 311, 24.6, 'N1XD4AR', 'S08'],
                    [31, 32, 27.7, 'N1XD9AR', 'S09'],
                    [32, 321, 39.9, 'NAYBY', 'S10'],
                    [32, 33, 118.8, 'NAYBY', 'S11'],
                    [1, 41, 56, 'NAYBY', 'S12'],
                    [1, 51, 216.6, 'NAYBY', 'S13'],
                    [51, 511, 132.8, 'N1XD9AR', 'S14'],
                    [511, 5111, 140.1, 'N1XD9AR', 'S15'],
                    [511, 5112, 66.4, 'NA2XY', 'S16'],
                    [511, 5113, 134.9, 'NAYBY', 'S17'],
                    [51, 52, 28.8, 'NAYBY', 'S18'],
                    [52, 521, 29.9, 'NAYBY', 'S19'],
                    [52, 522, 41.8, 'NAYBY', 'S20'],
                    [52, 53, 149.1, 'NAYBY', 'S21'],
                    [1, 61, 121.4, 'NAYBY', 'S22'],
                    [61, 611, 10.6, 'NAYBY', 'S23'],
                    [61, 62, 33, 'N1XD4AR', 'S24'],
                    [62, 621, 27.9, 'N1XD9AR', 'S25'],
                    [62, 622, 45.2, 'NAYBY', 'S26'],
                    [62, 63, 32.5, 'N1XD4AR', 'S27'],
                    [63, 631, 52.3, 'NAYBY', 'S28'],
                    [63, 64, 34.2, 'N1XD4AR', 'S29'],
                    [64, 641, 32.5, 'N1XD4AR', 'S30'],
                    [641, 6411, 86.3, 'NAYY', 'S31'],
                    [641, 6412, 19.9, 'NAYY', 'S32'],
                    [641, 6413, 97.9, 'N1XD4AR', 'S33'],
                    [64, 642, 89.6, 'NA2XY', 'S34'],
                    [64, 65, 26.4, 'N1XD4AR', 'S35'],
                    [65, 651, 21, 'NAYBY', 'S36'],
                    [65, 66, 76.5, 'N1XD4AR', 'S37'],
                    [1, 71, 36, 'N1XD4AR', 'S38']]

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
                 ['S05', 64.1],
                 ['S06', 172.5],
                 ['S08', 24.6],
                 ['S10', 39.9],
                 ['S11', 95.3],
                 ['S11', 118.8],
                 ['S12', 27.1],
                 ['S12', 56],
                 ['S15', 27.4],
                 ['S15', 76.8],
                 ['S15', 140.1],
                 # two loads on one bus: will be added later
                 ['S16', 66.4],
                 ['S17', 134.9],
                 ['S18', 28.8],
                 ['S19', 29.9],
                 ['S20', 34.6],
                 ['S20', 41.8],
                 ['S21', 62.5],
                 ['S21', 103.9],
                 ['S21', 133.1],
                 ['S21', 149.1],
                 ['S23', 10.6],
                 ['S26', 11.4],
                 ['S24', 33],
                 ['S25', 27.9],
                 ['S28', 13],
                 ['S28', 52.3],
                 ['S29', 34.2],
                 ['S31', 47.3],
                 ['S31', 86.3],
                 ['S32', 19.9],
                 ['S33', 97.9],
                 ['S34', 89.6],
                 ['S36', 21],
                 ['S37', 24.8],
                 ['S37', 38.7],
                 ['S37', 76.5]]

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
                    [3, 6],
                    [4, 14],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    [4, 17],
                    # two loads on one bus: will be added later
                    [4, 14],
                    [4, 14],
                    [4, 17],
                    [4, 17],
                    [4, 14],
                    [4, 17],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 14],
                    [4, 17],
                    [3, 6],
                    [4, 17],
                    [2, 14],
                    [1, 6],
                    [4, 14],
                    [4, 17],
                    [4, 14],
                    [1, 6],
                    [4, 14],
                    [2, 6],
                    [4, 14]]

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
    pp.create_load(net, bus=dict_of_buses['11'], p_mw=0.017, q_mvar=0, sn_mva=0.017, name='11', scaling=1.0, index=None,
                   in_service=True, type='wye')
    # create loads
    i = 0
    for loads_bus in buses_of_loads:
        b = dict_of_buses[loads_bus]
        loads_consumption = consumptions[i][1]
        loads_phase = consumptions[i][0]

        avg = loads_consumption / 1  # BE CAREFUL!!!!! these are the max values, to get a converged flow, use for
        # example loads_consumption/1000
        pp.create_load(net, bus=b, p_mw=avg / 1000, q_mvar=0, sn_mva=loads_consumption / 1000, name=loads_bus,
                       scaling=1.0, index=None, in_service=True, type='wye')

        # HERE: add the extra load, to the bus that has more than 1 load
        if loads_bus == "5111":
            pp.create_load(net, bus=b, p_mw=avg / 1000, q_mvar=0, sn_mva=loads_consumption / 1000, name=f"{loads_bus}b",
                           scaling=1.0, index=None, in_service=True, type='wye')

    # create last load
    pp.create_load(net, bus=dict_of_buses['1'], p_mw=0.011, q_mvar=0, sn_mva=0.011, name='1', scaling=1.0, index=None,
                   in_service=True, type='wye')

    # renam loads by MeterNo.
    net = network.besnica.besnica_rename_them_all.rename_loads(net)

    # create lines
    dict_of_lines = {}  # this dict contains the names as keys and the pp line objects as data
    for line in all_network_as_graph:
        act = all_network_as_graph[line]
        dict_of_lines[line] = pp.create_line(net, from_bus=dict_of_buses[str(act[0])],
                                             to_bus=dict_of_buses[str(act[1])], length_km=act[2] / 1000,
                                             std_type=act[3], name=line)

    # adds the zero sequence parameters of the standard types to the net model
    pp.add_zero_impedance_parameters(net)

    # run three-phase power flow pp.runpp(net, calculate_voltage_angles=True, init='auto', max_iteration='auto',
    # tolerance_mva=1e-08, enforce_q_lims=False, numba=True, recycle=None, check_connectivity=True,
    # switch_rx_ratio=2.0, delta_q=0, v_debug=False)
    return net
