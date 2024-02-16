from logging import getLogger

import pandapower as pp

from network.medium_voltage.line import LineObject


# Child of LineObject
class AssistantLineObject(LineObject):
    @staticmethod
    def create_in_pp(list_of_objects, net, object_name, vn):
        for li in list_of_objects:
            buses = []
            for i in li.xy.index:
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{li.fid}_{i}',
                                           geodata=(li.xy['EOV X'][i], li.xy['EOV Y'][i])))
            for i, b in enumerate(buses[1:]):
                pp.create_line(net, from_bus=buses[i], to_bus=b, length_km=0.001,
                               std_type="assist", name=f'{object_name}_{li.fid}_{i}')
            li.buses = buses

    # connecting method of AssistantLineObject
    # it only connects nodes, assistant lines, connectors and devices because of the order
    @staticmethod
    def connect_other_objects(dict_of_assist_objects, dict_of_conn_objects,
                              dict_of_node_objects, dict_of_dev_objects,
                              closest_i_j, net):
        for key_a in dict_of_assist_objects:
            own_list = []
            assist_obj = dict_of_assist_objects[key_a]
            for i in range(len(assist_obj.connected_objects.index.tolist())):
                name = assist_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Segédvezeték-KÖF':
                    # Kapcsolódó objektum példány
                    new_fid = assist_obj.connected_objects.iloc[i, 1]
                    if f"{str(new_fid)}_{str(key_a)}" in own_list:
                        pass
                    else:
                        own_list.append(f"{str(key_a)}_{str(new_fid)}")
                        try:
                            i_min, j_min = closest_i_j(assist_obj.xy,
                                                       dict_of_assist_objects[new_fid].xy)
                            pp.create_switch(net, bus=assist_obj.buses[i_min],
                                             element=dict_of_assist_objects[new_fid].buses[j_min],
                                             et='b', type='CB')
                        except KeyError as k:
                            getLogger("network_builder.medium_voltage").warning(
                                f"Segédvezetéknél van kapcsolódó másik, de nincs leképezve: {k}")
                elif name == 'Ele-Kapcsoló berendezés hely-KÖF':
                    new_fid = assist_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, _ = closest_i_j(assist_obj.xy, dict_of_conn_objects[new_fid].xy)
                        pp.create_switch(net, bus=assist_obj.buses[i_min],
                                         element=dict_of_conn_objects[new_fid].buses[
                                             dict_of_conn_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_conn_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Segédvezetéknél van kapcsoló, de kapcsolóknál nincs: {k}")
                elif name == 'Ele-Gyűjtősín-KÖF':
                    new_fid = assist_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, j_min = closest_i_j(assist_obj.xy, dict_of_node_objects[new_fid].xy)
                        pp.create_switch(net, bus=assist_obj.buses[i_min],
                                         element=dict_of_node_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Segédvezetéknél van gyűjtősín, de gyűjtősíneknél nincs: {k}")
                elif name == 'Ele-Készülék hely-KÖF':
                    new_fid = assist_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, _ = closest_i_j(assist_obj.xy, dict_of_dev_objects[new_fid].xy)
                        pp.create_switch(net, bus=assist_obj.buses[i_min],
                                         element=dict_of_dev_objects[new_fid].buses[
                                             dict_of_dev_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Segédvezetéknél van készülék, de készülékeknél nincs: {k}")
                else:
                    # MÉRŐVÁLTÓ, KIF objektum
                    pass

    # Accepting one way connections
    @staticmethod
    def fix(assists_to_check, dict_of_assist_objects, dict_of_tr_objects,
            dict_of_line_objects, closest_i_j, net):
        for key_a in assists_to_check:
            assist_obj = dict_of_assist_objects[key_a]
            for i in range(len(assist_obj.connected_objects.index.tolist())):
                new_fid = assist_obj.connected_objects.iloc[i, 1]
                name = assist_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Vezeték szakasz-KÖF':
                    try:
                        if key_a not in dict_of_line_objects[new_fid].connected_objects.iloc[:, 1]:
                            i_min, j_min = closest_i_j(assist_obj.xy,
                                                       dict_of_line_objects[new_fid].xy)
                            pp.create_switch(net, bus=assist_obj.buses[i_min],
                                             element=dict_of_line_objects[new_fid].buses[j_min],
                                             et='b', type='CB')
                    except KeyError as k:
                        log_str = 'Segédvezetéknél van vezeték, de vezetékeknél nincs: {}\n'
                        with open("network_builder_log.log", "a") as f:
                            f.write(log_str.format(k))
                elif name == 'Ele-Transzformátor hely':
                    if key_a not in dict_of_tr_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(assist_obj.xy, dict_of_tr_objects[new_fid].xy)
                        pp.create_switch(net, bus=assist_obj.buses[i_min],
                                         element=dict_of_tr_objects[new_fid].buses[0],
                                         et='b', type='CB')
