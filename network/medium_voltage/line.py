from logging import getLogger

import pandapower as pp

import utility.configuration as configuration
from network.medium_voltage.node import NodeObject


# Child of NodeObject
class LineObject(NodeObject):
    @staticmethod
    def collect_objects(objects, objects_graph, Object):
        # collect nodes
        list_of_objects = []
        list_of_fids = objects['FID'].drop_duplicates().tolist()
        for fid in list_of_fids:
            connected_objects = objects[['Kapcsolódó Objektum név',
                                         'Kapcsolódó Objketum példány']][objects['FID'] == fid]
            xy = objects_graph[['EOV X', 'EOV Y']][objects_graph['FID'] == fid]
            if configuration.config.getboolean('network', 'merge_lines_for_speed'):
                xy_indexes = xy.index.tolist()
                if len(xy_indexes) > 2:
                    xy = xy.drop(labels=xy_indexes[1:-1], axis=0)
            list_of_objects.append(Object(fid, connected_objects, xy))
        return list_of_objects

    @staticmethod
    def get_type_and_length(fid, frame):
        raw_string = frame[frame['FID'] == fid]['Típus Ele Vezeték szakasz TYPE 000E'].iloc[0]
        length = frame[frame['FID'] == fid]['Tényleges hossz m '].iloc[0]
        string = '_'
        for i in range(len(raw_string)):
            if raw_string[i] == '/':
                string += 'per'
            elif raw_string[i] == ' ':
                string += '_'
            elif raw_string[i] == '(':
                string += 'openingbracket'
            elif raw_string[i] == ')':
                string += 'closingbracket'
            elif raw_string[i] == 'ő' or raw_string[i] == 'ö':
                string += 'o'
            elif raw_string[i] == 'á':
                string += 'a'
            elif raw_string[i] == 'é':
                string += 'e'
            elif raw_string[i] == '*' or raw_string[i] == '×':
                string += 'star'
            else:
                string += raw_string[i]
        return string, length

    @staticmethod
    def create_in_pp(list_of_objects, net, object_name, vn, frame):
        for li in list_of_objects:
            string, length_m = LineObject.get_type_and_length(li.fid, frame)
            x_ys = []
            buses = []
            for i in li.xy.index:
                x, y = li.xy['EOV X'][i], li.xy['EOV Y'][i]
                x_ys.append((x, y))
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{li.fid}_{i}',
                                           geodata=(x, y)))
            x_y_lengths = []
            for i, x_y in enumerate(x_ys[1:]):
                x1 = x_ys[i][0]
                x2 = x_y[0]
                y1 = x_ys[i][1]
                y2 = x_y[1]
                x_y_lengths.append(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
            full_x_y = sum(x_y_lengths)
            for i, b in enumerate(buses[1:]):
                l_km = x_y_lengths[i] * length_m / (full_x_y * 1000)
                if l_km < 1e-4:
                    getLogger("network_builder.medium_voltage").warning(
                        f"Line '{object_name}_{li.fid}_{i}' length is close to zero. Setting length to a"
                        f" small dummy value, 1 m.")
                    l_km = 0.0001
                pp.create_line(net, from_bus=buses[i], to_bus=b, length_km=l_km, std_type=string,
                               name=f'{object_name}_{li.fid}_{i}')
            li.buses = buses

    # connecting method of LineObject
    # it only connects nodes, assistant lines, lines, connectors and devices because of the order
    @staticmethod
    def connect_other_objects(dict_of_line_objects, dict_of_assist_objects,
                              dict_of_conn_objects, dict_of_node_objects,
                              dict_of_dev_objects, closest_i_j, net):
        for key_l in dict_of_line_objects:
            own_list = []
            line_obj = dict_of_line_objects[key_l]
            for i in range(len(line_obj.connected_objects.index.tolist())):
                name = line_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Vezeték szakasz-KÖF':
                    # Kapcsolódó objektum példány
                    new_fid = line_obj.connected_objects.iloc[i, 1]
                    if f"{str(new_fid)}_{str(key_l)}" in own_list:
                        pass
                    else:
                        own_list.append(f"{str(key_l)}_{str(new_fid)}")
                        i_min, j_min = closest_i_j(line_obj.xy, dict_of_line_objects[new_fid].xy)
                        pp.create_switch(net, bus=line_obj.buses[i_min],
                                         element=dict_of_line_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Segédvezeték-KÖF':
                    new_fid = line_obj.connected_objects.iloc[i, 1]
                    i_min, j_min = closest_i_j(line_obj.xy, dict_of_assist_objects[new_fid].xy)
                    pp.create_switch(net, bus=line_obj.buses[i_min],
                                     element=dict_of_assist_objects[new_fid].buses[j_min],
                                     et='b', type='CB')
                elif name == 'Ele-Kapcsoló berendezés hely-KÖF':
                    new_fid = line_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, _ = closest_i_j(line_obj.xy, dict_of_conn_objects[new_fid].xy)
                        pp.create_switch(net, bus=line_obj.buses[i_min],
                                         element=dict_of_conn_objects[new_fid].buses[
                                             dict_of_conn_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_conn_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Vezetéknél van kapcsoló, de kapcsolóknál nincs: {k}")
                elif name == 'Ele-Gyűjtősín-KÖF':
                    new_fid = line_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, j_min = closest_i_j(line_obj.xy, dict_of_node_objects[new_fid].xy)
                        pp.create_switch(net, bus=line_obj.buses[i_min],
                                         element=dict_of_node_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Vezetéknél van gyűjtősín, de gyűjtősíneknél nincs: {k}")
                elif name == 'Ele-Készülék hely-KÖF':
                    new_fid = line_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, _ = closest_i_j(line_obj.xy, dict_of_dev_objects[new_fid].xy)
                        pp.create_switch(net, bus=line_obj.buses[i_min],
                                         element=dict_of_dev_objects[new_fid].buses[
                                             dict_of_dev_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Vezetéknél van készülék, de készülékeknél nincs: {k}")
                else:
                    # MÉRŐVÁLTÓ, KIF objektum
                    pass
