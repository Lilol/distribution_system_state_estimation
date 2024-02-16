# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 01:59:36 2021

@author: gegeh
"""
import pandapower as pp


def corr_closest(net):
    pp.create_switch(net, bus=33, element=114, et='b', type='DS', name='x1')
    pp.create_switch(net, bus=117, element=184, et='b', type='DS', name='x2')
    pp.create_switch(net, bus=187, element=122, et='b', type='DS', name='x3')
    pp.create_switch(net, bus=125, element=118, et='b', type='DS', name='x4')
    pp.create_switch(net, bus=121, element=71, et='b', type='DS', name='x5')
    pp.create_switch(net, bus=71, element=151, et='b', type='DS', name='x6')
    pp.create_switch(net, bus=151, element=22, et='b', type='DS', name='x7')
    pp.create_switch(net, bus=22, element=156, et='b', type='DS', name='x8')
    pp.create_switch(net, bus=76, element=126, et='b', type='DS', name='x9')
    pp.create_switch(net, bus=164, element=34, et='b', type='DS', name='x10')
    pp.create_switch(net, bus=164, element=37, et='b', type='DS', name='x11')
    pp.create_switch(net, bus=41, element=147, et='b', type='DS', name='x12')
    pp.create_switch(net, bus=150, element=143, et='b', type='DS', name='x13')
    pp.create_switch(net, bus=146, element=138, et='b', type='DS', name='x14')
    pp.create_switch(net, bus=142, element=101, et='b', type='DS', name='x15')
    pp.create_switch(net, bus=64, element=105, et='b', type='DS', name='x16')
    pp.create_switch(net, bus=176, element=81, et='b', type='DS', name='x17')
    return net


def corr_cut_to_pieces(net):
    pp.create_switch(net, bus=45, element=168, et='b', type='DS', name='x1')
    pp.create_switch(net, bus=171, element=260, et='b', type='DS', name='x2')
    pp.create_switch(net, bus=263, element=177, et='b', type='DS', name='x3')
    pp.create_switch(net, bus=180, element=172, et='b', type='DS', name='x4')
    pp.create_switch(net, bus=176, element=100, et='b', type='DS', name='x5')
    pp.create_switch(net, bus=100, element=212, et='b', type='DS', name='x6')
    pp.create_switch(net, bus=212, element=33, et='b', type='DS', name='x7')
    pp.create_switch(net, bus=33, element=219, et='b', type='DS', name='x8')
    pp.create_switch(net, bus=105, element=181, et='b', type='DS', name='x9')
    pp.create_switch(net, bus=229, element=46, et='b', type='DS', name='x10')
    pp.create_switch(net, bus=229, element=49, et='b', type='DS', name='x11')
    pp.create_switch(net, bus=53, element=208, et='b', type='DS', name='x12')
    pp.create_switch(net, bus=211, element=204, et='b', type='DS', name='x13')
    pp.create_switch(net, bus=207, element=199, et='b', type='DS', name='x14')
    pp.create_switch(net, bus=203, element=154, et='b', type='DS', name='x15')
    pp.create_switch(net, bus=92, element=158, et='b', type='DS', name='x16')
    pp.create_switch(net, bus=251, element=111, et='b', type='DS', name='x17')

    pp.create_load(net, bus=96, p_mw=0.001, q_mvar=0.0, name=2111641746)
    return net


def corr_exact(net):
    pp.create_switch(net, bus=91, element=92, et='b', type='DS', name='x1')
    pp.create_switch(net, bus=151, element=152, et='b', type='DS', name='x1')
    # return net
