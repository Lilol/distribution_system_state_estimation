from logging import getLogger

import pandapower as pp

from network.medium_voltage.connector import ConnectorObject


# Child of ConnectorObject
class DeviceObject(ConnectorObject):
    # connecting method of DeviceObject
    # it only connects devices because of the order
    @staticmethod
    def connect_other_objects(dict_of_dev_objects, closest_i_j, net):
        for key_v in dict_of_dev_objects:
            own_list = []
            dev_obj = dict_of_dev_objects[key_v]
            for i in range(len(dev_obj.connected_objects.index.tolist())):
                name = dev_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                if name == 'Ele-Készülék hely-KÖF':
                    # Kapcsolódó objektum példány
                    new_fid = dev_obj.connected_objects.iloc[i, 1]
                    if f"{str(new_fid)}_{str(key_v)}" in own_list:
                        pass
                    else:
                        own_list.append(f"{str(key_v)}_{str(new_fid)}")
                        try:
                            if (int(new_fid), int(dev_obj.fid)) not in dev_obj.connected_same_tuples:
                                pp.create_switch(net, bus=dev_obj.buses[dev_obj.next_bus_to_connect],
                                                 element=dict_of_dev_objects[new_fid].buses[
                                                     dict_of_dev_objects[new_fid].next_bus_to_connect],
                                                 et='b', type='CB')
                                dev_obj.next_bus_to_connect += 1
                                dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                                dict_of_dev_objects[new_fid].connected_same_tuples.append(
                                    (int(dev_obj.fid), int(new_fid)))
                            else:
                                pass
                        except KeyError as k:
                            getLogger("network_builder.medium_voltage").warning(
                                f"Készüléknél van kapcsolódó másik, de nincs leképezve: {k}")
                else:
                    # MÉRŐVÁLTÓ, KIF objektum
                    pass

    # Accept one way connection
    @staticmethod
    def fix(devs_to_check, dict_of_dev_objects, dict_of_line_objects,
            dict_of_assist_objects, dict_of_conn_objects, dict_of_node_objects,
            dict_of_tr_objects, closest_i_j, net):
        for key_d in devs_to_check:
            dev_obj = dict_of_dev_objects[key_d]
            for i in range(len(dev_obj.connected_objects.index.tolist())):
                name = dev_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                new_fid = dev_obj.connected_objects.iloc[i, 1]
                if name == 'Ele-Vezeték szakasz-KÖF':
                    if key_d not in dict_of_line_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(dev_obj.xy, dict_of_line_objects[new_fid].xy)
                        pp.create_switch(net, bus=dev_obj.buses[i_min],
                                         element=dict_of_line_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Segédvezeték-KÖF':
                    if key_d not in dict_of_assist_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(dev_obj.xy,
                                                   dict_of_assist_objects[new_fid].xy)
                        pp.create_switch(net, bus=dev_obj.buses[i_min],
                                         element=dict_of_assist_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Kapcsoló berendezés hely-KÖF':
                    if key_d not in dict_of_conn_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(dev_obj.xy, dict_of_conn_objects[new_fid].xy)
                        pp.create_switch(net, bus=dev_obj.buses[i_min],
                                         element=dict_of_conn_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Gyűjtősín-KÖF':
                    if key_d not in dict_of_node_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(dev_obj.xy, dict_of_node_objects[new_fid].xy)
                        pp.create_switch(net, bus=dev_obj.buses[i_min],
                                         element=dict_of_node_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                elif name == 'Ele-Transzformátor hely':
                    if key_d not in dict_of_tr_objects[new_fid].connected_objects.iloc[:, 1]:
                        i_min, j_min = closest_i_j(dev_obj.xy, dict_of_tr_objects[new_fid].xy)
                        pp.create_switch(net, bus=dev_obj.buses[i_min],
                                         element=dict_of_tr_objects[new_fid].buses[0],
                                         et='b', type='CB')
