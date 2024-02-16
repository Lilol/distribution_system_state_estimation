# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 14:14:29 2021

@author: Gergő
"""
import re
from os.path import join

import pandapower as pp
import pandas as pd

import utility.configuration as configuration
from network.definitions import NetworkId
from network.network_kind_string import get_network_kind_string
from network.pilot import corr_20667
from network.pilot import find_connectors
from network.pilot import find_transformer_2
from network.pilot import loads_and_lines
from network.pilot.exact_networks.build_exact import build_exact
# This function is used in every *.py file. It returns the only sheet of the Excel file which is specified by the
# argument.
from network.pilot.loads_and_lines import get_lines_sheet


def line_type_converter(string_of_line_type):
    string_of_line_type_to_return = ''
    for character in string_of_line_type:
        if character == ' ':
            string_of_line_type_to_return += '_'
        elif character == '+':
            string_of_line_type_to_return += 'plus'
        else:
            string_of_line_type_to_return += character
    return string_of_line_type_to_return


# This function gets the fid of a connector and returns its coordinates
def get_connectors_coords(connector_fid, path):
    connector_sheet_graph = get_lines_sheet('Kapcs_graf', path)
    for fid, x, y in zip(connector_sheet_graph['A'][2:], connector_sheet_graph['D'][2:],
                         connector_sheet_graph['F'][2:]):
        if fid.value == connector_fid:
            return x.value, y.value
    device_sheet_graph = get_lines_sheet('Kesz_graf', path)
    for fid, x, y in zip(device_sheet_graph['A'][2:], device_sheet_graph['E'][2:], device_sheet_graph['F'][2:]):
        if fid.value == connector_fid:
            return x.value, y.value
    raise RuntimeError(f"Invalid connector_fid {connector_fid}")


# This function gets the connector in form ['2120909745_0', 2120910856], the lines in form {2120911123: 
# [[544430.69435, 544404.86835, 544377.17735, 544369.50685], [168482.1442, 168476.3667, 168452.8057, 
# 168427.1692]], 2120909339: [[544455.17085,... and the path. It returns the index of the nearest bus for the
# connector. If this bus is the last bus of the whole line, it is shown by the last_flag.
def find_nearest_breakpoints_index_for_connector(connector, lines_of_the_network, path):
    connector_fid = int(connector[0].split('_')[0])
    line_fid = connector[1]
    x, y = get_connectors_coords(connector_fid, path)
    distances = []
    for possible_x, possible_y in zip(lines_of_the_network[line_fid][0], lines_of_the_network[line_fid][1]):
        distances.append((possible_x - x) ** 2 + (possible_y - y) ** 2)
    minimum = min(distances)
    index = distances.index(minimum)
    if index + 1 == len(distances):
        last_flag = True
        return index - 1, last_flag
    else:
        last_flag = False
        return index, last_flag


def calculate_shift(vector_group):
    match = re.search(r"[0-9]+", vector_group)
    if match:
        # For example: Dyn11 returns 11*30=330, Yy5 returns 5*30=150
        return int(match.group()) * 30
    else:
        raise RuntimeError(f"Invalid vector group string: {vector_group}")


def get_seconder_voltage_ratio(path):
    transformer_sheet = get_lines_sheet(f"Tr_{path[-5:]}", path)
    return transformer_sheet['I3'].value / 0.4


def calculate_length_ratios(coordinates):
    # Tuples represents coordinates of points.
    x_y_tuples = list(zip(coordinates[0], coordinates[1]))
    # The lengths are calculated for every part with Pythagoras Thesis
    lengths = []
    for i in range(len(x_y_tuples) - 1):
        x_0 = x_y_tuples[i][0]
        y_0 = x_y_tuples[i][1]
        x_1 = x_y_tuples[i + 1][0]
        y_1 = x_y_tuples[i + 1][1]
        lengths.append(((x_0 - x_1) ** 2 + (y_0 - y_1) ** 2) ** 0.5)
    sum_of_lengths = sum(lengths)
    normed_lengths = [length / sum_of_lengths for length in lengths]
    # return the normed lengths with the whole length (these are the ratios)
    return normed_lengths


def create_lines_by_fid_and_coordinates(fid, coordinates, net, dict_of_line_buses, path):
    # The list where the pp.line objects will be appended.
    created_parts = []
    # Get the Excel sheet.
    line_sheet = get_lines_sheet(f"Vezetek_{path[-5:]}", path)
    # just to enter the while loop
    fid_in_sheet = 0
    # start from 3rd row
    row = 3
    # iterate in fids while not getting our fid
    while fid_in_sheet != fid:
        fid_in_sheet = line_sheet[f"A{str(row)}"].value
        row += 1
    row -= 1
    # When the row is found, get the length of the line
    length = line_sheet[f"D{str(row)}"].value
    line_type = line_type_converter(line_sheet[f"F{str(row)}"].value)
    # From N coordinates we get N ratios. For example N=5; length_ratios=[0.2, 0.2, 0.2, 0.1, 0.3]
    length_ratios = calculate_length_ratios(coordinates)
    # get (X, Y) coordinates
    x_y_tuples = list(zip(coordinates[0], coordinates[1]))
    # iterate on them
    for i in range(len(x_y_tuples) - 1):
        # get the 2 buses by naming convention based on coordinates
        x_0 = x_y_tuples[i][0]
        y_0 = x_y_tuples[i][1]
        x_1 = x_y_tuples[i + 1][0]
        y_1 = x_y_tuples[i + 1][1]
        bus_to_connect = dict_of_line_buses[f"x:{str(x_0)}_y:{str(y_0)}"]
        connecting_bus = dict_of_line_buses[f"x:{str(x_1)}_y:{str(y_1)}"]
        # the length of the part can be calculted with the whole length and the ratio
        actual_length = length * length_ratios[i] / 1000
        # the partial lines are indexed from 0 to N-1 if there are N breakpoints
        name_of_part = f"{str(fid)}_{str(i)}"
        created_part = pp.create_line(net, from_bus=bus_to_connect, to_bus=connecting_bus, length_km=actual_length,
                                      std_type=line_type, name=name_of_part)
        created_parts.append(created_part)
    return created_parts


def find_the_nearest_breakpoints_key(lines_of_the_network, load_bus_name):
    # get the loads X, Y as string
    load_x = float(load_bus_name.split('_')[2].split(':')[1])
    load_y = float(load_bus_name.split('_')[3].split(':')[1])
    # The loads buses naming convention contains the fid of the object (line) where the actual load bus is connected.
    # So, the connecting line can be found by that.
    line = 0  # TODO
    for line in lines_of_the_network:
        try:
            if line == int(load_bus_name.split('_')[1].split(':')[1]):
                break
        except:
            pass
    # Different breakpoints have different distances from loads buses, so this section finds the nearest one and
    # returns it in the key format.
    distances = []
    for x, y in zip(lines_of_the_network[line][0], lines_of_the_network[line][1]):
        distances.append((x - load_x) ** 2 + (y - load_y) ** 2)
    minimum = min(distances)
    index = distances.index(minimum)
    return f"x:{str(lines_of_the_network[line][0][index])}_y:{str(lines_of_the_network[line][1][index])}"


def build(path):
    # Creating data: loads_of_the_network, that format is: [(1047120530, 'Ele-Vezeték szakasz-KIF', 1047085398,
    # 543700, 262657, 0.003637306695894642, '0', '0'), (1047120547, 'Ele... That is a list of tuples created from
    # Fogyasztok_123456_SAP_adatokkal Excel. At 1st index the consumers ID (fid number) can be found, At 2nd the type
    # of the element where the load is connected. At 3rd the ID (fid) of the element where the load is connected,
    # altough, if the type wasnt a line, the nearest lines fid is given here. At 4th the EOV (Egységes országos
    # vetület) X coordinate. At 5th the EOV (Egységes országos vetület) Y coordinate. At 6th the nominal power of the
    # load in MW. 7th is 1/0 if there is/isnt a "HMKE" here, 8th is 1/0 if there is/isn't a "vezérelt fogyasztó" here

    # Creating datas: lines_of_the_network, that format is: {2120911123: [[544430.69435, 544404.86835, 544377.17735,
    # 544369.50685], [168482.1442, 168476.3667, 168452.8057, 168427.1692]], 2120909339: [[544455.17085,... That is a
    # dict about KIF-modell-Vezetek_graf_vonalkoord_torespontokkal_123456. The keys are the fids of the lines and for
    # every key, there are 2 lists in 1 list. The first list contains the X coordinates of the breakpoints,
    # the second list contains the Y coordinates of the breakpoints in EOV.
    lines_of_the_network, loads_of_the_network = loads_and_lines.create_pilot_network(path)

    # transformers_of_the_networks format is: {2120910540: (544429.7208545865, 168589.8878663122), 2120910276: (
    # 544429.7942483264, 168589.8138550298), 2120910856:... It is a dict, where the keys are the lines fids where the
    # transformers seconder side is connected, and the values are tuples: (X, Y) coordinates, to identify the
    # breakpoint inside the line, where the transformer is connected.
    transformers_of_the_network = find_transformer_2.find(path)

    # connectors_of_the_network format is: [['2120909745_0', 2120910856], ['2120911053_0', 2120910510],
    # ['2120910917_0',... Its a 2D list where the inner list contains 2 elements: ID of the switch and fid of the
    # line where it is connected ..._0, ..._1, indexing is needed, because the KIF-modell-Kapcs_123456 and the
    # KIF-modell-Kesz_123456 seems redundant
    '''redundant'''
    # There are more than one place where a single switch is connected. And this happens many times.
    connectors_of_the_network = find_connectors.find(path)

    # show the mentioned data
    if configuration.config.getboolean("network", "print_results"):
        print(loads_of_the_network, end="\n\n")
        print(lines_of_the_network, end="\n\n")
        print(transformers_of_the_network, end="\n\n")
        print(connectors_of_the_network, end="\n\n")

    # empty net
    net = pp.create_empty_network()

    # May occur that, seconder voltage is not 400V. In that case it is r*400V. (correction)
    r = get_seconder_voltage_ratio(path)

    dict_of_line_buses = {}
    # Fill the dict.
    for line in lines_of_the_network:
        # For every breakpoint, there is a bus. Naming convention is: X:123.4_Y:567.89.
        for x, y in zip(lines_of_the_network[line][0], lines_of_the_network[line][1]):
            dict_of_line_buses[f"x:{str(x)}_y:{str(y)}"] = None
    bus_index = 0
    for bus in dict_of_line_buses:
        # Here, the correction of the LV can be seen in 'r'.
        x = float(bus.split('_')[0].split(':')[1])
        y = float(bus.split('_')[1].split(':')[1])
        dict_of_line_buses[bus] = pp.create_bus(net, vn_kv=0.4 * r, name=bus_index, geodata=(x, y))
        if bus_index == 187:
            k = 99
        bus_index += 1
    # so all in all the buses order in pp is: buses for loads 1...[num_of_loads] and buses for normal lines [
    # num_of_loads] + 1....[num_of_loads] + [num_of_normal_lines_buses]

    # assistant_line_type: This line is a ~0 impedance line to connect loads buses, and transformers LV side to the
    # breakpoints.
    assistline = {"r_ohm_per_km": 0.001, "x_ohm_per_km": 0.001, "c_nf_per_km": 0, "max_i_ka": 1000,
                  "r0_ohm_per_km": 0.001, "x0_ohm_per_km": 0.001, "c0_nf_per_km": 0}
    pp.create_std_type(net, assistline, name="ASSISTLINE", element="line")
    # line types of the four pilot project 
    _4x95Al = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.34, "c_nf_per_km": 0, "max_i_ka": 0.25, "r0_ohm_per_km": 1.244,
               "x0_ohm_per_km": 1.36, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Al, name="4x95_Al", element="line")
    _4x95Ml = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.071, "c_nf_per_km": 0, "max_i_ka": 0.16, "r0_ohm_per_km": 1.244,
               "x0_ohm_per_km": 0.284, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Ml, name="4x95_ML", element="line")
    _4x50Al = {"r_ohm_per_km": 0.603, "x_ohm_per_km": 0.357, "c_nf_per_km": 0, "max_i_ka": 0.16, "r0_ohm_per_km": 2.412,
               "x0_ohm_per_km": 1.428, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x50Al, name="4x50_Al", element="line")
    _10_Al_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _10_Al_plus_25_Al, name="10_Al_plus_25_Al", element="line")
    _3x10_Al_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _3x10_Al_plus_25_Al, name="3x10_Al_plus_25_Al", element="line")
    _3x10_ML_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.091, "c_nf_per_km": 0, "max_i_ka": 32}
    pp.create_std_type(net, _3x10_ML_plus_25_Al, name="3x10_ML_plus_25_Al", element="line")
    _3x16_Al = {"r_ohm_per_km": 1.83, "x_ohm_per_km": 0.39, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _3x16_Al, name="3x16_Al", element="line")
    _3x16_Al_plus_25_Al = {"r_ohm_per_km": 1.83, "x_ohm_per_km": 0.39, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _3x16_Al_plus_25_Al, name="3x16_Al_plus_25_Al", element="line")
    _3x240_Al_kbl_plus_120_Al_kbl = {"r_ohm_per_km": 0.125, "x_ohm_per_km": 0.088, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _3x240_Al_kbl_plus_120_Al_kbl, name="3x240_Al_kbl_plus_120_Al_kbl", element="line")
    _3x70_Al_plus_50_Al = {"r_ohm_per_km": 0.447, "x_ohm_per_km": 0.35, "c_nf_per_km": 0, "max_i_ka": 200}
    pp.create_std_type(net, _3x70_Al_plus_50_Al, name="3x70_Al_plus_50_Al", element="line")
    _4x10_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _4x10_Al, name="4x10_Al", element="line")
    _4x10_ML = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.091, "c_nf_per_km": 0, "max_i_ka": 32}
    pp.create_std_type(net, _4x10_ML, name="4x10_ML", element="line")
    _4x120_Al_kbl = {"r_ohm_per_km": 0.253, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 160}
    pp.create_std_type(net, _4x120_Al_kbl, name="4x120_Al_kbl", element="line")
    _4x150_Al_kbl = {"r_ohm_per_km": 0.206, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 200}
    pp.create_std_type(net, _4x150_Al_kbl, name="4x150_Al_kbl", element="line")
    _4x185_Al_kbl = {"r_ohm_per_km": 0.164, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _4x185_Al_kbl, name="4x185_Al_kbl", element="line")
    _4x240_Al_kbl = {"r_ohm_per_km": 0.125, "x_ohm_per_km": 0.088, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _4x240_Al_kbl, name="4x240_Al_kbl", element="line")
    _4x25_Al = {"r_ohm_per_km": 1.2, "x_ohm_per_km": 0.38, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x25_Al, name="4x25_Al", element="line")
    _4x25_ML = {"r_ohm_per_km": 1.2, "x_ohm_per_km": 0.078, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _4x25_ML, name="4x25_ML", element="line")
    _4x35_ML = {"r_ohm_per_km": 0.867, "x_ohm_per_km": 0.078, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _4x35_ML, name="4x35_ML", element="line")
    _4x50_Al_kbl = {"r_ohm_per_km": 0.641, "x_ohm_per_km": 0.093, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x50_Al_kbl, name="4x50_Al_kbl", element="line")
    _4x50_ML = {"r_ohm_per_km": 0.617, "x_ohm_per_km": 0.073, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x50_ML, name="4x50_ML", element="line")
    _4x95_Al_kbl = {"r_ohm_per_km": 0.32, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 125}
    pp.create_std_type(net, _4x95_Al_kbl, name="4x95_Al_kbl", element="line")

    # create loads to the correct buses by skipping the assistant lines
    for load in loads_of_the_network:
        # The naming convention is that: FID:123456_ConnectedLine:9876543210_X:123.4_Y:567.89
        load_bus_name = '_'.join(
            [f"fid:{str(load[0])}", f"obj:{str(load[2])}", f"x:{str(load[3])}", f"y:{str(load[4])}"])
        bus_to_connect = dict_of_line_buses[find_the_nearest_breakpoints_key(lines_of_the_network, load_bus_name)]
        pp.create_load(net, bus=bus_to_connect, name=load[0], p_mw=load[5] / 10)
        # this division can be used if we want converged load flow: p_mw = load[5]/100 (the nominal power is much
        # more than average)

    # Create the real lines: Fill a dict, where the keys are the fids of the lines (the lines which has breakpoints)
    # And the values are lists that contain pp.line objects
    partial_lines_dict = {}
    for line_fid in lines_of_the_network:
        # The sum of the partial lines (partial because of the breakpoints) length, gives the whole lines length.
        partial_lines_dict[line_fid] = create_lines_by_fid_and_coordinates(line_fid, lines_of_the_network[line_fid],
                                                                           net, dict_of_line_buses, path)
    # so all in all the lines order is: assistant lines for loads 1...[num_of_loads] and normal lines [num_of_loads]
    # + 1....[num_of_loads] + [num_of_normal_lines]

    # create transformer, and transformers buses (Like et Bóly network), and external grid
    df = pd.read_excel(join(path, "Trafo_datas.xlsx"), engine='openpyxl', skiprows=range(1, 2), sheet_name="Tr")
    '''I presume a file like Trafo_datas.xlsx where there will be data given like that. To be continued... '''
    # Trafo data
    trafo_data = {'vn_hv_kv': df.at[0, "Ur1"], 'vn_lv_kv': df.at[0, "Ur2"],
                  'vk_percent': df.at[0, "ukr(1)"], 'vkr_percent': df.at[0, "uRr(1)"],
                  'vk0_percent': df.at[0, "ukr(0)"], 'vkr0_percent': df.at[0, "uRr(0)"],
                  'sn_mva': df.at[0, "Sr"] / 1000, 'i0_percent': df.at[0, "I0"],
                  'vector_group': df.at[0, "Vektorcsoport"], "shift_degree": calculate_shift(df.at[0, "Vektorcsoport"]),
                  'pfe_kw': df.at[0, "Pvas"]}
    # create type for the trafo
    pp.create_std_type(net, trafo_data, name=df.at[0, "Típus"], element='trafo')
    # Create buses for transformer
    trafo_mv_side = pp.create_bus(net, vn_kv=df.at[0, "Ur1"], name="Trafo MV")
    trafo_lv_side = pp.create_bus(net, vn_kv=df.at[0, "Ur2"], name="Trafo LV")
    # Create bus for external grid
    bus0 = pp.create_bus(net, vn_kv=df.at[0, "Ur1"], name="Ext grid")
    pp.create_transformer(net, hv_bus=trafo_mv_side, lv_bus=trafo_lv_side, std_type=df.at[0, "Típus"])
    # Create external grid and switch
    pp.create_ext_grid(net, bus=bus0)
    pp.create_switch(net, bus=bus0, element=trafo_mv_side, et='b', closed=True, type='CB', name='S1')

    # connect the networks lines to the trnasformer
    bus_to_connect = trafo_lv_side
    # iterate on the dict, and connect by naming convention based on coordinates
    for key in transformers_of_the_network:
        x, y = transformers_of_the_network[key]
        connecting_bus = dict_of_line_buses[f"x:{str(x)}_y:{str(y)}"]
        # fuse the transformer LV buses, there will be n missing bus index in dataframe (there are n districts)
        pp.fuse_buses(net, bus_to_connect, connecting_bus, drop=True, fuse_bus_measurements=True)

    # create switches
    # iterate on this 2D list
    for connector in connectors_of_the_network:
        # find the correct partial line for the connector, if the connector is at the last partial lines to bus it is
        # shown by the last_flag
        index, last_flag = find_nearest_breakpoints_index_for_connector(connector, lines_of_the_network, path)
        partial_line = partial_lines_dict[connector[1]][index]
        if not last_flag:
            bus_for_switch = net.line.from_bus[partial_line]
        else:
            bus_for_switch = net.line.to_bus[partial_line]
        # the naming convention is the fid of the connector and the index
        '''remember: redundant'''
        pp.create_switch(net, bus=bus_for_switch, element=partial_line, et='l', type='CB', name=connector[0])

    pp.add_zero_impedance_parameters(net)

    # correction of EON files
    if configuration.config.get("input", "network_id") == NetworkId.ID_20667:
        network_kind = get_network_kind_string()
        if network_kind == 'closest':
            net = corr_20667.corr_closest(net)
        elif network_kind == 'cut_to_pieces':
            net = corr_20667.corr_cut_to_pieces(net)
        else:
            raise ValueError(f"Incorrect network kind: {network_kind}")

    # print network and run power flow
    if configuration.config.getboolean("network", "print_results"):
        print(net.line)
        print(net.bus)
        print(net.trafo)
        pp.runpp(net, calculate_voltage_angles=True, init='auto', max_iteration='auto', tolerance_mva=1e-08,
                 enforce_q_lims=False, numba=True, recycle=None, check_connectivity=True, switch_rx_ratio=2.0,
                 delta_q=0,
                 v_debug=False)
        print(net.res_bus.vm_pu)
        print(net.res_line.loading_percent)

    return net


def preprocess_network():
    path = configuration.config.get("paths", "pilot_path")
    if configuration.config.getboolean("network", "build_exact"):
        net = build_exact(path)
    else:
        net = build(path)
    return net
