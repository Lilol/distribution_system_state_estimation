from logging import getLogger

import pandapower as pp

from network.medium_voltage.node import NodeObject


# Child of NodeObject
class TransformerObject(NodeObject):
    @staticmethod
    def get_type(fid, frame):
        raw_str = frame[frame['FID'] == fid]['Típus Ele Transzformátor General TYPE 000E'].iloc[0]
        string = '_'
        for i in range(len(raw_str)):
            if raw_str[i] == '/':
                string += 'per'
            elif raw_str[i] in [' ', '-']:
                string += '_'
            elif raw_str[i] == 'é':
                string += 'e'
            elif raw_str[i] == '.':
                string += 'dot'
            else:
                string += raw_str[i]
        return string

    @staticmethod
    def create_in_pp(list_of_objects, net, frame, vn):
        # create transformers
        for t in list_of_objects:
            string = TransformerObject.get_type(t.fid, frame)
            hv_bus = pp.create_bus(net, vn_kv=vn,
                                   name=f'tr_{t.fid}_hv',
                                   geodata=(float(t.xy['EOV X']),
                                            float(t.xy['EOV Y'])))
            lv_bus = pp.create_bus(net, vn_kv=0.4,
                                   name=f'tr_{t.fid}_lv',
                                   geodata=(float(t.xy['EOV X']),
                                            float(t.xy['EOV Y'])))
            pp.create_transformer(net, hv_bus=hv_bus, lv_bus=lv_bus, name=t.fid, std_type=string)
            t.buses = [hv_bus, lv_bus]

    # Connecting method of transformers
    @staticmethod
    def connect_other_objects(dict_of_tr_objects, dict_of_line_objects, dict_of_assist_objects,
                              dict_of_conn_objects, dict_of_node_objects, dict_of_dev_objects,
                              closest_i_j, net):
        for key_t in dict_of_tr_objects:
            tr_obj = dict_of_tr_objects[key_t]
            for i in range(len(tr_obj.connected_objects.index.tolist())):
                new_fid = tr_obj.connected_objects.iloc[i, 1]
                try:
                    name = tr_obj.connected_objects.iloc[i]['Kapcsolódó Objektum név']
                    if name == 'Ele-Készülék hely-KÖF':
                        i_min, _ = closest_i_j(tr_obj.xy, dict_of_dev_objects[new_fid].xy)
                        pp.create_switch(net, bus=tr_obj.buses[i_min],
                                         element=dict_of_dev_objects[new_fid].buses[
                                             dict_of_dev_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_dev_objects[new_fid].next_bus_to_connect += 1
                    elif name == 'Ele-Gyűjtősín-KÖF':
                        i_min, j_min = closest_i_j(tr_obj.xy, dict_of_node_objects[new_fid].xy)
                        pp.create_switch(net, bus=tr_obj.buses[0],
                                         element=dict_of_node_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                    elif name == 'Ele-Kapcsoló berendezés hely-KÖF':
                        i_min, _ = closest_i_j(tr_obj.xy, dict_of_conn_objects[new_fid].xy)
                        pp.create_switch(net, bus=tr_obj.buses[i_min],
                                         element=dict_of_conn_objects[new_fid].buses[
                                             dict_of_conn_objects[new_fid].next_bus_to_connect],
                                         et='b', type='CB')
                        dict_of_conn_objects[new_fid].next_bus_to_connect += 1
                    elif name == 'Ele-Segédvezeték-KÖF':
                        i_min, j_min = closest_i_j(tr_obj.xy, dict_of_assist_objects[new_fid].xy)
                        pp.create_switch(net, bus=tr_obj.buses[0],
                                         element=dict_of_assist_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                    elif name == 'Ele-Vezeték szakasz-KÖF':
                        i_min, j_min = closest_i_j(tr_obj.xy, dict_of_line_objects[new_fid].xy)
                        pp.create_switch(net, bus=tr_obj.buses[0],
                                         element=dict_of_line_objects[new_fid].buses[j_min],
                                         et='b', type='CB')
                except KeyError as k:
                    getLogger("network_builder.medium_voltage").warning(f'A {new_fid} trafó nem köthető be: {k}')
