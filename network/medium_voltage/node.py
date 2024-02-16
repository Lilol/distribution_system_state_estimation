from logging import getLogger

import pandapower as pp


# Base object:í fid, connected objects, x-y coordinates, buses
# It is the parent of ConnectorObject, LineObject, TrasformerObject
class NodeObject:
    def __init__(self, fid, connected_objects, xy, buses=None):
        self.fid = fid
        self.connected_objects = connected_objects
        self.xy = xy
        self.buses = buses

    @staticmethod
    def collect_objects(objects, objects_graph, Object):
        # collect nodes
        list_of_objects = []
        list_of_fids = objects['FID'].drop_duplicates().tolist()
        for fid in list_of_fids:
            connected_objects = objects[['Kapcsolódó Objektum név',
                                         'Kapcsolódó Objketum példány']][objects['FID'] == fid]
            xy = objects_graph[['EOV X', 'EOV Y']][objects_graph['FID'] == fid]
            list_of_objects.append(Object(fid, connected_objects, xy))
        return list_of_objects

    @staticmethod
    def create_in_pp(list_of_objects, net, object_name, vn):
        # create buses from nodes
        for o in list_of_objects:
            buses = []
            for i in o.xy.index:
                buses.append(pp.create_bus(net, vn_kv=vn,
                                           name=f'{object_name}_{o.fid}_{i}',
                                           geodata=(o.xy['EOV X'][i], o.xy['EOV Y'][i])))
            # connect same buses
            if len(buses) > 1:
                for i, b in enumerate(buses[1:]):
                    pp.create_switch(net, bus=buses[0], element=b, et='b', type='CB',
                                     name=f'{object_name}_{o.fid}_{i}')
            o.buses = buses

    # create dict from list with fid keys
    @staticmethod
    def create_dict_of_objects(list_of_objects):
        return {o.fid: o for o in list_of_objects}

    # connecting method of NodeObject
    # it only connects nodes and devices because of the order
    @staticmethod
    def connect_other_objects(dict_of_node_objects, dict_of_dev_objects, closest_i_j, net):
        for key_n in dict_of_node_objects:
            own_list = []
            node_obj = dict_of_node_objects[key_n]
            for i in range(len(node_obj.connected_objects.index.tolist())):
                name = node_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Gyűjtősín-KÖF':
                    # Kapcsolódó objektum példány
                    new_fid = node_obj.connected_objects.iloc[i, 1]
                    if f"{str(new_fid)}_{str(key_n)}" in own_list:
                        pass
                    else:
                        own_list.append(f"{str(key_n)}_{str(new_fid)}")
                        try:
                            i_min, j_min = closest_i_j(node_obj.xy,
                                                       dict_of_node_objects[new_fid].xy)
                            pp.create_switch(net, bus=node_obj.buses[i_min],
                                             element=dict_of_node_objects[new_fid].buses[j_min],
                                             et='b', type='CB')
                        except KeyError as k:
                            getLogger("network_builder.medium_voltage").warning(
                                f"Gyűjtősínnel van kapcsolódó másik, de nincs leképezve: {k}")
                elif name == 'Ele-Készülék hely-KÖF':
                    new_fid = node_obj.connected_objects.iloc[i, 1]
                    try:
                        i_min, _ = closest_i_j(node_obj.xy, dict_of_dev_objects[new_fid].xy)
                        pp.create_switch(net, bus=node_obj.buses[i_min],
                                         element=dict_of_dev_objects[new_fid].buses[
                                             dict_of_dev_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                    except KeyError as k:
                        getLogger("network_builder.medium_voltage").warning(
                            f"Gyűjtősínnél van készülék, de készülékeknél nincs: {k}")
                else:
                    # MÉRŐVÁLTÓ, KIF objektum
                    pass

    # Accept one way connections
    @staticmethod
    def fix(nodes_to_check, dict_of_node_objects, dict_of_line_objects,
            dict_of_assist_objects, dict_of_conn_objects, dict_of_tr_objects,
            closest_i_j, net):
        for key_n in nodes_to_check:
            node_obj = dict_of_node_objects[key_n]
            for i in range(len(node_obj.connected_objects.index.tolist())):
                new_fid = node_obj.connected_objects.iloc[i, 1]
                name = node_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Vezeték szakasz-KÖF':
                    if key_n not in dict_of_line_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(node_obj.xy, dict_of_line_objects[new_fid].xy)
                        pp.create_switch(net, bus=node_obj.buses[i_min],
                                         element=dict_of_line_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Segédvezeték-KÖF':
                    if key_n not in dict_of_assist_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(node_obj.xy, dict_of_assist_objects[new_fid].xy)
                        pp.create_switch(net, bus=node_obj.buses[i_min],
                                         element=dict_of_assist_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Kapcsoló berendezés hely-KÖF':
                    if key_n not in dict_of_conn_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(node_obj.xy, dict_of_conn_objects[new_fid].xy)
                        pp.create_switch(net, bus=node_obj.buses[i_min],
                                         element=dict_of_conn_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Transzformátor hely':
                    if key_n not in dict_of_tr_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(node_obj.xy, dict_of_tr_objects[new_fid].xy)
                        pp.create_switch(net, bus=node_obj.buses[i_min],
                                         element=dict_of_tr_objects[new_fid].buses[0],
                                         et='b', type='CB')
