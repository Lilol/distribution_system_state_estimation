# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 00:12:47 2021

@author: Gergő
"""
# This function is used in every *.py file. It returns the only sheet of the Excel file which is specified by the
# argument.
from network.pilot.loads_and_lines import get_lines_sheet

# There are more than one place where a single switch is connected. And this happens many times.
'''indexing because the mentioned redundant values'''


def indexing_fids(fid_object_pairs):
    # the drop_duplicated function returned: [[0123456789, 0246813579], ...]
    # thi function makes: [['0123456789_0', 0246813579], ...]
    fids = {}  # make a dict for counting
    for f in range(len(fid_object_pairs)):
        # In case of first element: 0 index
        if fid_object_pairs[f][0] not in fids:
            fids[fid_object_pairs[f][0]] = 1
            fid_object_pairs[f][0] = f"{str(fid_object_pairs[f][0])}_0"
        # In case of Nth element: N index
        else:
            key_for_dict = fid_object_pairs[f][0]
            fid_object_pairs[f][0] = '_'.join([str(fid_object_pairs[f][0]), str(fids[fid_object_pairs[f][0]])])
            fids[key_for_dict] += 1
    return fid_object_pairs


# This function drops the duplication if we found device-line or connector-line pair more then once
def drop_duplicated(list_2d_with_2_columns):
    values = []
    for r in list_2d_with_2_columns:
        # add only the first element
        if f"{str(r[0])}_{str(r[1])}" in values:
            pass
        else:
            values.append(f"{str(r[0])}_{str(r[1])}")
    # make 2 integers in a list from a string: '0123456789_0246813579' -> [0123456789, 0246813579]
    for i in range(len(values)):
        values[i] = [int(x) for x in values[i].split('_')]
    # and th list will be: [[0123456789, 0246813579], ...]
    return values


# This function is a bit different from the function in loades_and_lines.py. The difference can be found
# incontact_type == 'Ele-Transzformátor hely'. This function works recursively. Gets an object, its type and sheets.
# And returns the connected 'Ele-Vezeték szakasz-KIF' to the object
def find_recursively(fids, contact_types, node_sheet, assistant_line_sheet, device_sheet, already_found):
    zipped = zip(fids, contact_types)
    # fids and contact_types for next recursion
    next_fids = []
    next_contact_types = []
    for fid, contact_type in zipped:
        # Looping on objects fid, and type. For every object we open the correct sheet, defined by its type. For
        # 'Ele-Gyűjtősín-KIF': node_sheet, for 'Ele-Segédvezeték-KIF': assistant_line_sheet, for 'Ele-Készülék
        # hely-KIF': device_sheet Then we are searching for new objects (types and fids) If we find
        # 'Ele-Gyűjtősín-KIF', 'Ele-Segédvezeték-KIF' or 'Ele-Készülék hely-KIF': give them to list, call recursion (
        # last row) If we find 'Ele-Transzformátor hely': wrong way, we search FOR this, not this If we find
        # 'Ele-Vezeték szakasz-KIF': we finished: return its fid
        if contact_type == 'Ele-Gyűjtősín-KIF':
            row_list = [i.value for i in node_sheet['A']]
            rows = [i for i, x in enumerate(row_list) if x == fid]
            new_contact_types = [node_sheet[f"G{str(row + 1)}"].value for row in rows]
            new_fids = [node_sheet[f"H{str(row + 1)}"].value for row in rows]
        elif contact_type == 'Ele-Segédvezeték-KIF':
            row_list = [i.value for i in assistant_line_sheet['A']]
            rows = [i for i, x in enumerate(row_list) if x == fid]
            new_contact_types = [assistant_line_sheet[f"G{str(row + 1)}"].value for row in rows]
            new_fids = [assistant_line_sheet[f"H{str(row + 1)}"].value for row in rows]
        elif contact_type == 'Ele-Készülék hely-KIF':
            row_list = [i.value for i in device_sheet['A']]
            rows = [i for i, x in enumerate(row_list) if x == fid]
            new_contact_types = [device_sheet[f"J{str(row + 1)}"].value for row in rows]
            new_fids = [device_sheet[f"K{str(row + 1)}"].value for row in rows]
        elif contact_type == 'Ele-Transzformátor hely':
            new_contact_types = []
            new_fids = []
        elif contact_type == 'Ele-Vezeték szakasz-KIF':
            return fid
        else:
            raise RuntimeError(f"Invalid contact type: {contact_type}")

        next_contact_types += new_contact_types
        next_fids += new_fids
    return find_recursively(next_fids, next_contact_types, node_sheet, assistant_line_sheet, device_sheet,
                            already_found)


# This function returns:
# [['2120909745_0', 2120910856], ['2120911053_0', 2120910510], ['2120910917_0',...
# Its a 2D list where the inner list contains 2 elements: ID of the switch and fid of the line where it is connected
# ..._0, ..._1, indexing is needed, because the KIF-modell-Kapcs_123456 and the KIF-modell-Kesz_123456 seems redundant
# There are more than one place where a single switch is connected. And this happens many times.
'''redundant'''


def find(path):
    already_found = []
    # get KIF-modell-Gys_12345.xlsx
    node_sheet = get_lines_sheet(f"Gys_{path[-5:]}", path)
    # get KIF-modell-Segedvez_12345.xlsx
    assistant_line_sheet = get_lines_sheet(f"Segedvez_{path[-5:]}", path)
    # get KIF-modell-Kesz_12345.xlsx
    device_sheet = get_lines_sheet(f"Kesz_{path[-5:]}", path)
    # Search line for every device
    device_zipped_objname_obj = zip(device_sheet['J'][2:], device_sheet['K'][2:])
    for n, o in device_zipped_objname_obj:
        already_found.append(find_recursively([o.value], [n.value], node_sheet, assistant_line_sheet, device_sheet,
                                              already_found))
    for i in range(len(already_found)):
        already_found[i] = [device_sheet['A'][i + 2].value, already_found[i]]
    # get KIF-modell-Kapcs_12345.xlsx
    connector_sheet = get_lines_sheet(f"Kapcs_{path[-5:]}", path)
    connector_zipped_objname_obj = zip(connector_sheet['A'][2:], connector_sheet['I'][2:], connector_sheet['J'][2:])
    # Search line for every connector
    for fid, n, o in connector_zipped_objname_obj:
        if 'Vezeték' in n.value:
            already_found.append([fid.value, o.value])
    # If we found a device-line or connector-line pair more then once, drop the duplication
    already_found = drop_duplicated(already_found)
    '''indexing because the mentioned redundant values'''
    already_found = indexing_fids(already_found)
    return already_found
