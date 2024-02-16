# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 11:22:13 2021

@author: Gergő
"""

# copy/pasted from Excel
new_names = [4028558,
             4028557,
             4016776,
             4029988,
             4028559,
             4028561,
             4028562,
             4028565,
             4028564,
             4029985]


def rename_asymmetric_loads(net):
    i = 0
    for n in net.asymmetric_load.name:
        idx = net.asymmetric_load[net.asymmetric_load.name == n].index[0]
        net.asymmetric_load.name.at[idx] = new_names[i]
        i += 1
    return net


def rename_loads(net):
    i = 0
    for n in net.load.name:
        idx = net.load[net.load.name == n].index[0]
        net.load.name.at[idx] = new_names[i]
        i += 1
    return net

#
# idx = net.asymmetric_load[net.asymmetric_load.name=="1201"].index[0]
# net.asymmetric_load.name.at[idx] = "Ujnev"
# another option net.asymmetric_load.at[idx, 'name'] = "Ujnev"
