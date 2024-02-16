# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 15:41:40 2021

@author: Gergő
"""


def sort_load_buses_as_consumtions(buses_of_loads):
    """Simple bubble-sort"""
    for bus in buses_of_loads:
        if len(bus[1]) == 3:
            bus[1] = f"{bus[1]}XX"
    for i in range(len(buses_of_loads) - 1, 0, -1):
        for j in range(0, i):
            if buses_of_loads[j + 1][1] < buses_of_loads[j][1]:
                temp = buses_of_loads[j]
                buses_of_loads[j] = buses_of_loads[j + 1]
                buses_of_loads[j + 1] = temp
    for element_i in range(len(buses_of_loads)):
        buses_of_loads[element_i] = buses_of_loads[element_i][0]
    return buses_of_loads


def buses_of_end_loads(end_loads, base_network):
    buses = []
    for line in base_network:
        if line[4] in end_loads:
            buses.append([str(line[1]), line[4]])
    return buses


def buses_of_mid_loads(base_dict):
    buses = []
    for line in base_dict:
        if str(base_dict[line][1])[-2] == "0":
            buses.append([str(base_dict[line][1]), line])
    return buses


def make_mid_dict(mid_buses):
    """ From this:
        [['S02', 40.5],
        ['S02', 86.6],
        .
        .
        .
        ['S37', 76.5]]
        
        To this:
        {'S02': 40.5,
         'S02': 86.6,
        .
        .
        .
         'S37': 76.5}
        """
    mid_dict = {}
    for line in mid_buses:
        mid_dict[line[0]] = []
    for line in mid_buses:
        mid_dict[line[0]].append(line[1])
    return mid_dict


def delete_ends_from_mid_dict(base_network, mid_dict):
    """Removes the buses, that are not mid-buses
    these are originally in the base_network.
    Also returns the names of the lines, that
    have loads on their ends."""
    end_loads = []
    for base_bus in base_network:
        try:
            mid_dict[base_bus[4]].remove(base_bus[2])
            end_loads.append(base_bus[4])
        except:
            pass
    empty = []
    for key in mid_dict:
        if not mid_dict[key]:
            empty.append(key)
    for key in empty:
        del mid_dict[key]
    return mid_dict, end_loads


def make_base_dict(base_network):
    """Returns this form of data:
        {'S01': [1, 11, 105, 'NAYBY'], 'S02':..."""
    base_dict = {}
    for line in base_network:
        base_dict[line[-1]] = line[0:-1]
    return base_dict


def create(base_network, mid_buses):
    mid_dict = make_mid_dict(mid_buses)
    mid_dict, end_loads = delete_ends_from_mid_dict(base_network, mid_dict)
    base_dict = make_base_dict(base_network)
    for line in mid_dict:
        # at this section mid_dicts lengths datas will be formed to be measured as a "chain" (part-by-part),
        # and not measured from the start point
        mid_dict[line].append(base_dict[line][2] - mid_dict[line][-1])  # the mid_dict gets the last part of line
        for length_i in range(-2, - len(mid_dict[line]), -1):
            mid_dict[line][length_i] = mid_dict[line][length_i] - mid_dict[line][
                length_i - 1]  # all the other chain parts
        # at this section base_dict datas will be merged, with mid_dict datas
        i = 1
        for piece in mid_dict[line]:
            base_dict[f"{line}0{str(i)}"] = []  # special name convesion of line that has loads
            if i == 1:  # the first part of this line
                base_dict[f"{line}0{str(i)}"] = [base_dict[line][0], base_dict[line][1] * 100 + i, piece,
                                                 base_dict[line][3]]
                before = base_dict[line][1] * 100 + i
            elif i == len(mid_dict[line]):  # last part
                base_dict[f"{line}0{str(i)}"] = [before, base_dict[line][1], piece, base_dict[line][3]]
            else:  # all the other parts
                base_dict[f"{line}0{str(i)}"] = [before, base_dict[line][1] * 100 + i, piece, base_dict[line][3]]
                before = base_dict[line][1] * 100 + i
            i += 1
    # now, the original lines that contain loads are splitted into correct, "chain/part-by-part" lines,
    # so the old ones has to be deleted
    keys_to_del = []
    for line in base_dict:
        if (f"{line}01") in base_dict:
            keys_to_del.append(line)
    for line in keys_to_del:
        del base_dict[line]
    buses_of_loads = buses_of_end_loads(end_loads, base_network) + buses_of_mid_loads(
        base_dict)  # this will be returned as well
    buses_of_loads = sort_load_buses_as_consumtions(buses_of_loads)
    return base_dict, buses_of_loads
