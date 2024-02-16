from logging import getLogger

import pandapower as pp

from network.medium_voltage.node import NodeObject


# Child of NodeObject
class ConnectorObject(NodeObject):
    def __init__(self, fid, connected_objects, xy, buses=None):
        super().__init__(fid, connected_objects, xy, buses=[])
        self.next_bus_to_connect = 0
        self.connected_same_tuples = []

    @staticmethod
    def create_in_pp(list_of_objects, net, object_name, vn):
        # a variable, to make easy to visualize the switches
        dist = 0
        # create buses from nodes
        for o in list_of_objects:
            buses = []
            for i in o.xy.index:
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{o.fid}_{i}',
                                           geodata=(o.xy['EOV X'][i] + dist, o.xy['EOV Y'][i])))
                dist += 0.1
            # connect same buses
            if len(buses) > 1:
                for i, b in enumerate(buses[1:]):
                    pp.create_switch(net, bus=buses[0], element=b,
                                     et='b', type='CB',
                                     name=f'{object_name}_{o.fid}_{i}')
            else:
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{o.fid}_{i}_second',
                                           geodata=(o.xy['EOV X'][i] + dist, o.xy['EOV Y'][i])))
                dist += 0.1
                pp.create_switch(net, bus=buses[0], element=buses[1], et='b', type='CB',
                                 name=f'{object_name}_{o.fid}_0')
            while len(o.connected_objects) > len(buses):
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{o.fid}_{i}_second',
                                           geodata=(o.xy['EOV X'][i] + dist, o.xy['EOV Y'][i])))
                dist += 0.1
                pp.create_switch(net, bus=buses[0], element=buses[-1], et='b', type='CB',
                                 name=f'{object_name}_{o.fid}_0')
            o.buses = buses

    # connecting method of ConnectorObject
    # it only connects nodes, connectors and devices because of the order
    @staticmethod
    def connect_other_objects(dict_of_conn_objects, dict_of_node_objects,
                              dict_of_dev_objects, closest_i_j, net):
        for key_c in dict_of_conn_objects:
            own_list = []
            conn_obj = dict_of_conn_objects[key_c]
            for i in range(len(conn_obj.connected_objects.index.tolist())):
                name = conn_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Kapcsoló berendezés hely-KÖF':
                    # Kapcsolódó objektum példány
                    new_fid = conn_obj.connected_objects.iloc[i, 1]
                    if f"{str(new_fid)}_{str(key_c)}" in own_list:
                        pass
                    else:
                        own_list.append(f"{str(key_c)}_{str(new_fid)}")
                        try:
                            # to avoid the 2-time increasing
                            if (int(new_fid), int(conn_obj.fid)) not in conn_obj.connected_same_tuples:
                                pp.create_switch(net, bus=conn_obj.buses[conn_obj.next_bus_to_connect],
                                                 element=dict_of_conn_objects[new_fid].buses[
                                                     dict_of_conn_objects[new_fid].next_bus_to_connect],
                                                 et='b', type='CB')
                                conn_obj.next_bus_to_connect += 1
                                dict_of_conn_objects[new_fid].next_bus_to_connect += 1
                                dict_of_conn_objects[new_fid].connected_same_tuples.append(
                                    (int(conn_obj.fid), int(new_fid)))
                            else:
                                pass
                        except KeyError as k:
                            getLogger("network_builder.medium_voltage").warning(
                                f"Kapcsolóval van kapcsolódó másik, de nincs leképezve: {k}")
                elif name == 'Ele-Gyűjtősín-KÖF':
                    new_fid = conn_obj.connected_objects.iloc[i, 1]
                    try:
                        _, j_min = closest_i_j(conn_obj.xy, dict_of_node_objects[new_fid].xy)
                        pp.create_switch(net, bus=conn_obj.buses[conn_obj.next_bus_to_connect],
                                         element=dict_of_node_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                        conn_obj.next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Kapcsolónál van gyűjtősín, de gyűjtősíneknél nincs: {k}")
                elif name == 'Ele-Készülék hely-KÖF':
                    new_fid = conn_obj.connected_objects.iloc[i, 1]
                    try:
                        pp.create_switch(net, bus=conn_obj.buses[conn_obj.next_bus_to_connect],
                                         element=dict_of_dev_objects[new_fid].buses[
                                             dict_of_dev_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        conn_obj.next_bus_to_connect += 1
                        dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Kapcsolónál van készülék, de készülékeknél nincs: {k}")
                else:
                    # MÉRŐVÁLTÓ, KIF objektum
                    pass

    # Accept one way connections
    @staticmethod
    def fix(conns_to_check, dict_of_conn_objects, dict_of_line_objects,
            dict_of_assist_objects, dict_of_tr_objects, closest_i_j, net):
        for key_c in conns_to_check:
            conn_obj = dict_of_conn_objects[key_c]
            for i in range(len(conn_obj.connected_objects.index.tolist())):
                new_fid = conn_obj.connected_objects.iloc[i, 1]
                name = conn_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Vezeték szakasz-KÖF':
                    if key_c not in dict_of_line_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(conn_obj.xy, dict_of_line_objects[new_fid].xy)
                        pp.create_switch(net, bus=conn_obj.buses[i_min],
                                         element=dict_of_line_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Segédvezeték-KÖF':
                    if key_c not in dict_of_assist_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(conn_obj.xy, dict_of_assist_objects[new_fid].xy)
                        pp.create_switch(net, bus=conn_obj.buses[i_min],
                                         element=dict_of_assist_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Transzformátor hely':
                    if key_c not in dict_of_tr_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(conn_obj.xy, dict_of_tr_objects[new_fid].xy)
                        pp.create_switch(net, bus=conn_obj.buses[i_min],
                                         element=dict_of_tr_objects[new_fid].buses[0],
                                         et='b', type='CB')
