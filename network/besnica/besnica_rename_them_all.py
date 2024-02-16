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
             4029985,
             4029984,
             4028568,
             4012546,
             4028571,
             4028570,
             4012543,
             4028569,
             4028547,
             4028548,
             4028549,
             4028550,
             4012562,
             4028551,
             4028574,
             4028575,
             4028573,
             4028572,
             4015946,
             4028586,
             4016770,
             4028593,
             4016773,
             4028609,
             4029987,
             4028577,
             4012558,
             4028584,
             4028595,
             4028582,
             4028581,
             4029986,
             4028578,
             4028590,
             4032628,
             4016774,
             4016777,
             4016775,
             4028567]


def rename_asymmetric_loads(net):
    i = 0
    for n in net.asymmetric_load.name:
        idx = net.asymmetric_load[net.asymmetric_load.name == n].index[0]
        net.asymmetric_load.name.at[idx] = new_names[i]
        i += 1
    return net


def rename_loads(net):
    net.load.name = new_names[0:len(net.load.name)]
    return net

#
# idx = net.asymmetric_load[net.asymmetric_load.name=="1201"].index[0]
# net.asymmetric_load.name.at[idx] = "Ujnev"
# another option net.asymmetric_load.at[idx, 'name'] = "Ujnev"
