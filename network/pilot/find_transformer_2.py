# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 00:12:47 2021

@author: Gergő
"""
# This function is used in every *.py file. It returns the only sheet of the Excel file which is specified by the
# argument.
from network.pilot.loads_and_lines import get_lines_sheet


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
        elif contact_type == 'Ele-Transzformátor hely' or fid in already_found:
            new_contact_types = []
            new_fids = []
        elif contact_type == 'Ele-Vezeték szakasz-KIF':
            return fid
        else:
            raise RuntimeError(f"Unknown contact_type:{contact_type}")
        next_contact_types += new_contact_types
        next_fids += new_fids
    return find_recursively(next_fids, next_contact_types, node_sheet, assistant_line_sheet, device_sheet,
                            already_found)


# This function returns: {2120910540: (544429.7208545865, 168589.8878663122), 2120910276: (544429.7942483264,
# 168589.8138550298), 2120910856:... It is a dict, where the keys are the lines fids where the transformers secunder
# side is connected, and the vaues are tuples: (X, Y) coordinates, to identify the breakpoint inside the line,
# where the transformer is connected.
def find(path):
    # Get the fid of the KIF side of the transformer from KIF-modell-Tr_12345.xlsx
    transformer_sheet = get_lines_sheet(f"Tr_{path[-5:]}", path)
    if "KIF" in transformer_sheet['K3'].value:
        fid = transformer_sheet['L3'].value
    else:
        fid = transformer_sheet['L4'].value
    # get KIF-modell-Gys_12345.xlsx
    node_sheet = get_lines_sheet(f"Gys_{path[-5:]}", path)
    # get KIF-modell-Segedvez_12345.xlsx
    assistant_line_sheet = get_lines_sheet(f"Segedvez_{path[-5:]}", path)
    # get KIF-modell-Kesz_12345.xlsx
    device_sheet = get_lines_sheet(f"Kesz_{path[-5:]}", path)
    # get KIF-modell-Vezetek_graf_vonalkoord_torespontokkal_12345.xlsx
    line_sheet = get_lines_sheet('Vezetek_graf', path)
    # get the numer of circuits from transformer LV side, for example: N1, N2, N3, N3b: 4 areas
    number_of_areas = len(list(set([n.value for n in line_sheet['C'][2:]])))
    already_found = {}
    # search an 'Ele-Vezeték szakasz-KIF' for every area
    for i in range(number_of_areas):
        new_fid = find_recursively([fid], ['Ele-Segédvezeték-KIF'], node_sheet, assistant_line_sheet, device_sheet,
                                   already_found)
        already_found[new_fid] = []
    # After we have the fids, we search the Xs and Ys for them and make a dict, and fill
    fids_column = [i.value for i in line_sheet['A']]
    x_coordinates_column = [i.value for i in line_sheet['J']]
    y_coordinates_column = [i.value for i in line_sheet['K']]
    zip_fid_x_y = zip(fids_column, x_coordinates_column, y_coordinates_column)
    for fid, x, y in zip_fid_x_y:
        if fid in already_found:
            already_found[fid].append((x, y))
    # After that we have to get the nearest part of the line (nearest breakpoint)
    # Then return it in a dict
    transformer_sheet = get_lines_sheet('Tr_graf', path)
    x_tr = transformer_sheet['C3'].value
    y_tr = transformer_sheet['D3'].value
    for key in already_found:
        distances = []
        for tup_x_y in already_found[key]:
            distance_square = (x_tr - tup_x_y[0]) ** 2 + (y_tr - tup_x_y[1]) ** 2
            distances.append(distance_square)
        min_index = distances.index(min(distances))
        already_found[key] = already_found[key][min_index]
    return already_found
