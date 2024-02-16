import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
from logging import getLogger

import openpyxl
import pandapower as pp
import pandas as pd

import utility.configuration as configuration
from network.definitions import HIGH_VOLTAGE_TRAFO_NAME, Network, NetworkId
from network.medium_voltage import add_five_number_data
from network.medium_voltage.assistant_line import AssistantLineObject
from network.medium_voltage.connector import ConnectorObject
from network.medium_voltage.device import DeviceObject
from network.medium_voltage.hv_transformer import HighVoltageTransformer
from network.medium_voltage.line import LineObject
from network.medium_voltage.line_type import LineTypes
from network.medium_voltage.node import NodeObject
from network.medium_voltage.transformer import TransformerObject
from network.medium_voltage.transformer_type import TransformerTypes
from network.utility import merge_lines_with_impedance_close_to_zero


# If the first row does not starts with FID, skip it
def skip_rows(file):
    wb = openpyxl.load_workbook(file)
    sheet_name = wb.get_sheet_names()[0]
    sheet = wb.get_sheet_by_name(sheet_name)
    if sheet['A1'].value == 'FID':
        return 0
    else:
        return 1


# Get a specified dataframe
def framer(key, area, path):
    # path of excel file
    import glob
    os.chdir(path)
    for file in glob.glob(f"*{key}_{area}.xlsx"):
        return pd.read_excel(file, sheet_name=0,
                             skiprows=skip_rows(file),
                             engine='openpyxl').drop_duplicates()


# Get the nominal voltage of the area
def find_vn(trs):
    return float(trs['Névleges feszültség primer k V '].mode())


# Squared Euclidean distance
def dist_square(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


# Get the closest rows of (EOV X, EOV Y)s from two frame
def closest_i_j(xy_frame_1, xy_frame_2):
    # first indexes
    i_min = xy_frame_1.index.min()
    j_min = xy_frame_2.index.min()
    x1 = xy_frame_1['EOV X'][i_min]
    x2 = xy_frame_2['EOV X'][j_min]
    y1 = xy_frame_1['EOV Y'][i_min]
    y2 = xy_frame_2['EOV Y'][j_min]
    # first distance
    minimum = dist_square(x1, y1, x2, y2)
    # find the smallest distance
    for i in xy_frame_1.index:
        for j in xy_frame_2.index:
            x1 = xy_frame_1['EOV X'][i]
            x2 = xy_frame_2['EOV X'][j]
            y1 = xy_frame_1['EOV Y'][i]
            y2 = xy_frame_2['EOV Y'][j]
            act = dist_square(x1, y1, x2, y2)
            if act < minimum:
                minimum = act
                i_min = i
                j_min = j
    return (xy_frame_1.index.tolist().index(i_min),
            xy_frame_2.index.tolist().index(j_min))


# Returns the indexes of small disjunt network parts
# and index of the main (biggest) part.
def get_indexes_of_small_disjunt_subdicts(diag_results):
    list_of_sizes = []
    for d in diag_results['disconnected_elements']:
        counter_for_size = 0
        for key in d:
            counter_for_size += len(d[key])
        list_of_sizes.append(counter_for_size)
    max_value = max(list_of_sizes)
    max_index = list_of_sizes.index(max_value)
    list_length = len(list_of_sizes)
    indexes = [index for index in range(list_length) if index != max_index]
    return indexes, max_index


# Merge all dicts
def dict_of_elements_to_be_checked(list_of_dicts):
    dict_of_elements = {'buses': [], 'lines': [], 'switches': []}
    for d in list_of_dicts:
        if 'buses' in d:
            dict_of_elements['buses'] += d['buses']
        if 'lines' in d:
            dict_of_elements['lines'] += d['lines']
        if 'switches' in d:
            dict_of_elements['switches'] += d['switches']
    return dict_of_elements


# Connect remaining elements to the closest ones
def solve_the_remaining_connect_problems(net):
    diag_results = pp.diagnostic(net, report_style=None)
    # indexes_of_small_disjunt_subdicts, max index
    indexes, max_index = get_indexes_of_small_disjunt_subdicts(diag_results)
    list_of_dicts = [diag_results['disconnected_elements'][i] for i in indexes]
    list_of_good_dicts = diag_results['disconnected_elements'][max_index]
    # LV buses cant be connecte to hv buses
    good_buses = list_of_good_dicts['buses']
    bus_list = net.bus['name'].tolist()
    for i, wrong_voltage in enumerate([('lv' in name) for name in bus_list]):
        if wrong_voltage and i in good_buses:
            good_buses.remove(i)
    # Connect to closest
    geodata = net.bus_geodata
    for dict_of_elements in list_of_dicts:
        bad_buses = dict_of_elements['buses']
        b1 = good_buses[0]
        b2 = bad_buses[0]
        pair = (0, 0)
        dmin = dist_square(geodata.iloc[b1]['x'], geodata.iloc[b1]['y'],
                           geodata.iloc[b2]['x'], geodata.iloc[b2]['y'])
        for b1 in good_buses:
            for b2 in bad_buses:
                x1 = geodata.iloc[b1]['x']
                x2 = geodata.iloc[b2]['x']
                y1 = geodata.iloc[b1]['y']
                y2 = geodata.iloc[b2]['y']
                d = dist_square(x1, y1, x2, y2)
                if d < dmin:
                    dmin = d
                    pair = (b1, b2)
        pp.create_switch(net, bus=pair[0], element=pair[1], et='b', type='CB')


# Delete unnecessary switches from lines, assistant lines
def filter_lines_and_assistant_line_switches(net):
    while True:
        real_switches = net.switch['name'].notnull()
        if all(real_switches):
            break

        for b1, b2, real_switch in zip(net.switch['bus'], net.switch['element'], real_switches):
            if not real_switch:
                pp.fuse_buses(net, b1, b2)
                break


# Delete unnecessary switches from nodes
def filter_node_switches(net):
    df = net.switch[net.switch['name'].notnull()]
    real_switches = (df['name'].str.contains("conn", case=False) |
                     df['name'].str.contains("start", case=False) |
                     df['name'].str.contains("dev", case=False)).tolist()
    for b1, b2, real_switch, name in zip(df['bus'].tolist(),
                                         df['element'].tolist(),
                                         real_switches,
                                         df['name'].tolist()):
        if not real_switch:
            if 'node' in name:
                net.bus.at[b1, 'name'] = name
            pp.fuse_buses(net, b1, b2)


# Delete unnecessary switches (the order is important)
def filter_switches(net):
    filter_lines_and_assistant_line_switches(net)
    filter_node_switches(net)


def create_external_grid(net, bus_to_create):
    if not bus_to_create:
        hv_trafo = HighVoltageTransformer()
        lv_string = f"{hv_trafo.connecting_type}_{hv_trafo.connecting_fid}"
        lv_bus = net.bus[net.bus['name'].str.contains(lv_string,
                                                      case=False)].index[0]
    else:
        lv_bus = bus_to_create
    pp.create_ext_grid(net, bus=lv_bus)
    return lv_bus


# Create the HV transformer and the external grid
def create_hvtr_and_ext_grid(net, hv_tr_secunder=None):
    lv_bus = create_external_grid(net, hv_tr_secunder)
    gdata = (net.bus_geodata.loc[lv_bus])

    hv_trafo = HighVoltageTransformer()
    hv_bus = pp.create_bus(net, vn_kv=hv_trafo.data['vn_hv_kv'], name="hv_tr_primer",
                           geodata=(gdata['x'], gdata['y']))

    pp.create_std_type(net, hv_trafo.data, name=hv_trafo.name, element='trafo')
    pp.create_transformer(net, hv_bus=hv_bus, lv_bus=lv_bus,
                          name=hv_trafo.name, std_type=hv_trafo.name)


def build():
    area = NetworkId(configuration.config.getint("network.medium_voltage", 'area')).value
    path = configuration.config.get("paths", "network_path")
    getLogger("network").info(f"Building network {area}")

    # Get the frames of excels
    nodes = framer('Gys', area, path)
    nodes_graph = framer('Gys_graf', area, path)
    conns = framer('Kapcs', area, path)
    conns_graph = framer('Kapcs_graf', area, path)
    devs = framer('Kesz', area, path)
    devs_graph = framer('Kesz_graf', area, path)
    assists = framer('Segedvez', area, path)
    assists_graph = framer('Segedvez_graf', area, path)
    trs = framer('Tr', area, path)
    trs_graph = framer('Tr_graf', area, path)
    lines = framer('Vezetek', area, path)
    lines_graph = framer('Vezetek_graf_vonalkoord_torespontokkal', area, path)
    vn = configuration.config.getfloat("network.medium_voltage", "voltage_level")

    # collect x objects to XObjects
    list_of_line_objects = LineObject.collect_objects(lines, lines_graph,
                                                      LineObject)
    list_of_assist_objects = AssistantLineObject.collect_objects(assists, assists_graph,
                                                                 AssistantLineObject)
    list_of_node_objects = NodeObject.collect_objects(nodes, nodes_graph,
                                                      NodeObject)
    list_of_conn_objects = ConnectorObject.collect_objects(conns, conns_graph,
                                                           ConnectorObject)
    list_of_dev_objects = DeviceObject.collect_objects(devs, devs_graph,
                                                       DeviceObject)
    list_of_tr_objects = TransformerObject.collect_objects(trs, trs_graph,
                                                           TransformerObject)
    # create empty network
    net = pp.create_empty_network()

    # create buses from nodes, devices, connectors
    NodeObject.create_in_pp(list_of_node_objects, net, 'node', vn)
    DeviceObject.create_in_pp(list_of_dev_objects, net, 'dev', vn)
    ConnectorObject.create_in_pp(list_of_conn_objects, net, 'conn', vn)

    # create lines, assistant lines
    dict_of_line_types = LineTypes().__dict__
    for key in dict_of_line_types:
        pp.create_std_type(net, data=dict_of_line_types[key], name=key, element="line")
    LineObject.create_in_pp(list_of_line_objects, net, 'line', vn, lines)

    AssistantLineObject.create_in_pp(list_of_assist_objects, net, 'assist', vn)

    # create transformers
    dict_of_tr_types = TransformerTypes(vn).__dict__
    for key in dict_of_tr_types:
        pp.create_std_type(net, dict_of_tr_types[key], name=key, element='trafo')
    TransformerObject.create_in_pp(list_of_tr_objects, net, trs, vn)

    # dicts
    dict_of_node_objects = NodeObject.create_dict_of_objects(list_of_node_objects)
    dict_of_conn_objects = ConnectorObject.create_dict_of_objects(list_of_conn_objects)
    dict_of_dev_objects = DeviceObject.create_dict_of_objects(list_of_dev_objects)
    dict_of_line_objects = LineObject.create_dict_of_objects(list_of_line_objects)
    dict_of_assist_objects = AssistantLineObject.create_dict_of_objects(list_of_assist_objects)
    dict_of_tr_objects = TransformerObject.create_dict_of_objects(list_of_tr_objects)

    # CONNECT EVERYTHING
    # LINES
    LineObject.connect_other_objects(dict_of_line_objects, dict_of_assist_objects,
                                     dict_of_conn_objects, dict_of_node_objects,
                                     dict_of_dev_objects, closest_i_j, net)
    # ASSISTANT LINES
    AssistantLineObject.connect_other_objects(dict_of_assist_objects, dict_of_conn_objects,
                                              dict_of_node_objects, dict_of_dev_objects,
                                              closest_i_j, net)
    # CONNECTORS
    ConnectorObject.connect_other_objects(dict_of_conn_objects, dict_of_node_objects,
                                          dict_of_dev_objects, closest_i_j, net)
    # NODES
    NodeObject.connect_other_objects(dict_of_node_objects, dict_of_dev_objects,
                                     closest_i_j, net)
    # DEVICES
    DeviceObject.connect_other_objects(dict_of_dev_objects, closest_i_j, net)

    # TRANSFORMERS
    TransformerObject.connect_other_objects(dict_of_tr_objects, dict_of_line_objects,
                                            dict_of_assist_objects, dict_of_conn_objects,
                                            dict_of_node_objects, dict_of_dev_objects,
                                            closest_i_j, net)
    create_hvtr_and_ext_grid(net)

    diag_results = pp.diagnostic(net, report_style=None)
    is_of_small_disjunct_subdicts, _ = get_indexes_of_small_disjunt_subdicts(diag_results)
    list_of_dicts = [diag_results['disconnected_elements'][i] for i in is_of_small_disjunct_subdicts]
    dict_of_elements = dict_of_elements_to_be_checked(list_of_dicts)
    if configuration.config.getboolean('network', 'fix'):
        # FIX PROBLEMS 1
        buses_to_check = [net.bus.iloc[b]['name'] for b in dict_of_elements['buses']]
        lines_to_check = [net.line.iloc[li]['name'] for li in dict_of_elements['lines']]
        switches_to_check = [net.switch.iloc[s]['name'] for s in dict_of_elements['switches']]
        # merge, remove duplicates, remove Nones
        merged_list = buses_to_check + lines_to_check + switches_to_check
        elements_to_check = list(filter(None, list(dict.fromkeys(merged_list))))
        nodes_to_check = [int(e.split('_')[1]) for e in elements_to_check if e.split('_')[0] == 'node']
        conns_to_check = [int(e.split('_')[1]) for e in elements_to_check if e.split('_')[0] == 'conn']
        devs_to_check = [int(e.split('_')[1]) for e in elements_to_check if e.split('_')[0] == 'dev']
        ass_to_check = [int(e.split('_')[1]) for e in elements_to_check if e.split('_')[0] == 'assist']
        # (transformers and lines were connected to everywhere before)

        # ASSIST AGAIN
        AssistantLineObject.fix(ass_to_check, dict_of_assist_objects, dict_of_tr_objects,
                                dict_of_line_objects, closest_i_j, net)

        # CONNECTOR AGAIN
        ConnectorObject.fix(conns_to_check, dict_of_conn_objects, dict_of_line_objects,
                            dict_of_assist_objects, dict_of_tr_objects, closest_i_j, net)

        # NODE AGAIN
        NodeObject.fix(nodes_to_check, dict_of_node_objects, dict_of_line_objects,
                       dict_of_assist_objects, dict_of_conn_objects, dict_of_tr_objects,
                       closest_i_j, net)

        # DEVICE AGAIN
        DeviceObject.fix(devs_to_check, dict_of_dev_objects, dict_of_line_objects,
                         dict_of_assist_objects, dict_of_conn_objects, dict_of_node_objects,
                         dict_of_tr_objects, closest_i_j, net)

        # FIX PROBLEMS 2
        solve_the_remaining_connect_problems(net)

    else:
        buses_to_delete = [b for b in dict_of_elements['buses']]
        pp.drop_buses(net, buses_to_delete)

    filter_switches(net)

    # Check for line impedances close to zero, and add switches as a replacement
    merge_lines_with_impedance_close_to_zero(net)
    pp.drop_out_of_service_elements(net)

    diag_results = pp.diagnostic(net, report_style=None)
    if 'parallel_switches' in diag_results:
        net.switch.drop((sw[0] for sw in diag_results["parallel_switches"]), inplace=True)

    add_load_to_transformers(net)
    # Rename LV buses of trafos as well
    net.bus.loc[net.trafo.lv_bus, "name"] = "tr_" + net.trafo.name.astype("str").values + "_lv"

    net.trafo.vn_lv_kv[net.trafo.vn_lv_kv == 21] = 22
    return net


def add_load_to_transformers(net):
    if net.trafo.empty:
        return

    for _, trafo in net.trafo[net.trafo.name != HIGH_VOLTAGE_TRAFO_NAME].iterrows():
        if not any(net.load.bus == trafo.lv_bus):
            pp.create_load(net, trafo.lv_bus, p_mw=0.001, const_z_percent=100, name=trafo["name"])
        if not any(net.sgen.bus == trafo.lv_bus):
            pp.create_sgen(net, trafo.lv_bus, p_mw=0.001, name=trafo["name"])


if __name__ == "__main__":
    build()
