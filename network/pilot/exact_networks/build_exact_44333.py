# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 09:47:53 2021

@author: Gergő
"""

import pandapower as pp

import utility.configuration as configuration


def create(path='.'):
    # empty net
    net = pp.create_empty_network()
    trafo_data = {'vn_hv_kv': 21, 'vn_lv_kv': 0.4,
                  'vk_percent': 5.834, 'vkr_percent': 1.4,
                  'vk0_percent': 5.834, 'vkr0_percent': 1.4,
                  'sn_mva': 0.4, 'i0_percent': 2.5,
                  'vector_group': 'Dyn5', "shift_degree": 150,
                  'pfe_kw': 0.83}

    # create type for the trafo
    pp.create_std_type(net, trafo_data, name='IE 35-140', element='trafo')
    trafo_mv_side = pp.create_bus(net, vn_kv=21, name="Trafo MV")
    trafo_lv_side = pp.create_bus(net, vn_kv=0.4, name="Trafo LV")

    # Create bus for external grid
    bus0 = pp.create_bus(net, vn_kv=21, name="Ext grid")
    pp.create_transformer(net, hv_bus=trafo_mv_side, lv_bus=trafo_lv_side, std_type='IE 35-140')

    # Create external grid and switch
    pp.create_ext_grid(net, bus=bus0)
    pp.create_switch(net, bus=bus0, element=trafo_mv_side, et='b', closed=True, type='CB', name='S1')
    _4x95Al = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.34, "c_nf_per_km": 0, "max_i_ka": 0.25,
               "r0_ohm_per_km": 1.244, "x0_ohm_per_km": 1.36, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Al, name="4x95 Al", element="line")
    _4x95Ml = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.071, "c_nf_per_km": 0, "max_i_ka": 0.16,
               "r0_ohm_per_km": 1.244, "x0_ohm_per_km": 0.284, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Ml, name="4x95 Ml", element="line")
    _4x50Al = {"r_ohm_per_km": 0.603, "x_ohm_per_km": 0.357, "c_nf_per_km": 0, "max_i_ka": 0.16,
               "r0_ohm_per_km": 2.412, "x0_ohm_per_km": 1.428, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x50Al, name="4x50 Al", element="line")
    _10_Al_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _10_Al_plus_25_Al, name="10_Al_plus_25_Al", element="line")
    _3x10_Al_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _3x10_Al_plus_25_Al, name="3x10_Al_plus_25_Al", element="line")
    _3x10_ML_plus_25_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.091, "c_nf_per_km": 0, "max_i_ka": 32}
    pp.create_std_type(net, _3x10_ML_plus_25_Al, name="3x10_ML_plus_25_Al", element="line")
    _3x16_Al = {"r_ohm_per_km": 1.83, "x_ohm_per_km": 0.39, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _3x16_Al, name="3x16_Al", element="line")
    _3x16_Al_plus_25_Al = {"r_ohm_per_km": 1.83, "x_ohm_per_km": 0.39, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _3x16_Al_plus_25_Al, name="3x16_Al_plus_25_Al", element="line")
    _3x240_Al_kbl_plus_120_Al_kbl = {"r_ohm_per_km": 0.125, "x_ohm_per_km": 0.088, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _3x240_Al_kbl_plus_120_Al_kbl, name="3x240_Al_kbl_plus_120_Al_kbl", element="line")
    _3x70_Al_plus_50_Al = {"r_ohm_per_km": 0.447, "x_ohm_per_km": 0.35, "c_nf_per_km": 0, "max_i_ka": 200}
    pp.create_std_type(net, _3x70_Al_plus_50_Al, name="3x70_Al_plus_50_Al", element="line")
    _4x10_Al = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.4, "c_nf_per_km": 0, "max_i_ka": 50}
    pp.create_std_type(net, _4x10_Al, name="4x10_Al", element="line")
    _4x10_ML = {"r_ohm_per_km": 3.08, "x_ohm_per_km": 0.091, "c_nf_per_km": 0, "max_i_ka": 32}
    pp.create_std_type(net, _4x10_ML, name="4x10_ML", element="line")
    _4x120_Al_kbl = {"r_ohm_per_km": 0.253, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 160}
    pp.create_std_type(net, _4x120_Al_kbl, name="4x120_Al_kbl", element="line")
    _4x150_Al_kbl = {"r_ohm_per_km": 0.206, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 200}
    pp.create_std_type(net, _4x150_Al_kbl, name="4x150_Al_kbl", element="line")
    _4x185_Al_kbl = {"r_ohm_per_km": 0.164, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _4x185_Al_kbl, name="4x185_Al_kbl", element="line")
    _4x240_Al_kbl = {"r_ohm_per_km": 0.125, "x_ohm_per_km": 0.088, "c_nf_per_km": 0, "max_i_ka": 250}
    pp.create_std_type(net, _4x240_Al_kbl, name="4x240_Al_kbl", element="line")
    _4x25_Al = {"r_ohm_per_km": 1.2, "x_ohm_per_km": 0.38, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x25_Al, name="4x25_Al", element="line")
    _4x25_ML = {"r_ohm_per_km": 1.2, "x_ohm_per_km": 0.078, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _4x25_ML, name="4x25_ML", element="line")
    _4x35_ML = {"r_ohm_per_km": 0.867, "x_ohm_per_km": 0.078, "c_nf_per_km": 0, "max_i_ka": 63}
    pp.create_std_type(net, _4x35_ML, name="4x35_ML", element="line")
    _4x50_Al_kbl = {"r_ohm_per_km": 0.641, "x_ohm_per_km": 0.093, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x50_Al_kbl, name="4x50_Al_kbl", element="line")
    _4x50_ML = {"r_ohm_per_km": 0.617, "x_ohm_per_km": 0.073, "c_nf_per_km": 0, "max_i_ka": 100}
    pp.create_std_type(net, _4x50_ML, name="4x50_ML", element="line")
    _4x95_Al_kbl = {"r_ohm_per_km": 0.32, "x_ohm_per_km": 0.09, "c_nf_per_km": 0, "max_i_ka": 125}
    pp.create_std_type(net, _4x95_Al_kbl, name="4x95_Al_kbl", element="line")

    # A trafótól át a hóvirág utca fölött az egyik oldalról a másik oldalra, majd jobbra a hóvirág utcán B1 leágazás
    b0 = pp.create_bus(net, vn_kv=0.4, name=0)
    pp.create_switch(net, bus=trafo_lv_side, element=b0, et='b', type='CB', name='B1')
    b1 = pp.create_bus(net, vn_kv=0.4, name=1)
    pp.create_line(net, from_bus=b0, to_bus=b1, length_km=0.015, std_type="4x95 Ml", name='0_1')
    pp.create_load(net, bus=b1, name=2120756183, p_mw=0.001)
    b2 = pp.create_bus(net, vn_kv=0.4, name=2)
    pp.create_line(net, from_bus=b1, to_bus=b2, length_km=0.0309, std_type="4x50 Al", name='1_2')
    pp.create_load(net, bus=b2, name=2120756808, p_mw=0.001)
    pp.create_load(net, bus=b2, name=2120754438, p_mw=0.001)
    b3 = pp.create_bus(net, vn_kv=0.4, name=3)
    pp.create_line(net, from_bus=b2, to_bus=b3, length_km=0.0387, std_type="4x50 Al", name='2_3')
    pp.create_load(net, bus=b3, name=2120755586, p_mw=0.001)
    pp.create_load(net, bus=b3, name=2120755542, p_mw=0.001)
    pp.create_load(net, bus=b3, name=2120755763, p_mw=0.001)
    pp.create_load(net, bus=b3, name=2120756184, p_mw=0.001)
    b4 = pp.create_bus(net, vn_kv=0.4, name=4)
    pp.create_line(net, from_bus=b3, to_bus=b4, length_km=0.0404, std_type="4x50 Al", name='3_4')
    pp.create_load(net, bus=b4, name=2120757024, p_mw=0.001)
    pp.create_load(net, bus=b4, name=2120755572, p_mw=0.001)
    pp.create_load(net, bus=b4, name=2120756930, p_mw=0.001)
    pp.create_load(net, bus=b4, name=2120754752, p_mw=0.001)
    b5 = pp.create_bus(net, vn_kv=0.4, name=5)
    pp.create_line(net, from_bus=b4, to_bus=b5, length_km=0.0387, std_type="4x50 Al", name='4_5')
    pp.create_load(net, bus=b5, name=2120754919, p_mw=0.001)
    pp.create_load(net, bus=b5, name=2120755597, p_mw=0.001)
    pp.create_load(net, bus=b5, name=2120756447, p_mw=0.001)
    pp.create_load(net, bus=b5, name=2120756937, p_mw=0.001)
    pp.create_load(net, bus=b2, name=2120754447, p_mw=0.001)
    b6 = pp.create_bus(net, vn_kv=0.4, name=6)
    pp.create_line(net, from_bus=b5, to_bus=b6, length_km=0.0393, std_type="4x50 Al", name='5_6')
    pp.create_load(net, bus=b6, name=2120756878, p_mw=0.001)
    pp.create_load(net, bus=b6, name=2120755532, p_mw=0.001)
    pp.create_load(net, bus=b6, name=2120754832, p_mw=0.001)
    b7 = pp.create_bus(net, vn_kv=0.4, name=7)
    pp.create_line(net, from_bus=b6, to_bus=b7, length_km=0.0348, std_type="4x50 Al", name='6_7')
    pp.create_load(net, bus=b7, name=1049691203, p_mw=0.001)
    b8 = pp.create_bus(net, vn_kv=0.4, name=8)
    pp.create_line(net, from_bus=b7, to_bus=b8, length_km=0.0203, std_type="4x50_ML", name='7_8')
    b9 = pp.create_bus(net, vn_kv=0.4, name=9)
    pp.create_line(net, from_bus=b8, to_bus=b9, length_km=0.0195, std_type="4x50_ML", name='8_9')
    pp.create_load(net, bus=b9, name=2120756039, p_mw=0.001)
    b10 = pp.create_bus(net, vn_kv=0.4, name=10)
    pp.create_line(net, from_bus=b9, to_bus=b10, length_km=0.0352, std_type="4x50_ML", name='9_10')
    pp.create_load(net, bus=b10, name=2120754928, p_mw=0.001)
    pp.create_load(net, bus=b10, name=2120756783, p_mw=0.001)
    b11 = pp.create_bus(net, vn_kv=0.4, name=11)
    pp.create_line(net, from_bus=b10, to_bus=b11, length_km=0.0354, std_type="4x50_ML", name='10_11')
    pp.create_load(net, bus=b11, name=2120756401, p_mw=0.001)
    pp.create_load(net, bus=b11, name=2120755711, p_mw=0.001)
    b12 = pp.create_bus(net, vn_kv=0.4, name=12)
    pp.create_line(net, from_bus=b11, to_bus=b12, length_km=0.0358, std_type="4x50_ML", name='11_12')
    pp.create_load(net, bus=b12, name=2120757085, p_mw=0.001)
    b13 = pp.create_bus(net, vn_kv=0.4, name=13)
    pp.create_line(net, from_bus=b12, to_bus=b13, length_km=0.0356, std_type="4x50_ML", name='12_13')
    pp.create_load(net, bus=b13, name=2120756312, p_mw=0.001)
    pp.create_load(net, bus=b13, name=2120754936, p_mw=0.001)
    pp.create_load(net, bus=b13, name=1080008310, p_mw=0.001)
    pp.create_load(net, bus=b13, name=2120754783, p_mw=0.001)

    # Visszakanyarodva lefele
    b14 = pp.create_bus(net, vn_kv=0.4, name=14)
    pp.create_line(net, from_bus=b13, to_bus=b14, length_km=0.0914, std_type="4x95_Al_kbl", name='13_14')
    pp.create_load(net, bus=b14, name=2120755285, p_mw=0.001)
    pp.create_load(net, bus=b14, name=2120756545, p_mw=0.001)
    pp.create_load(net, bus=b14, name=2120755495, p_mw=0.001)
    pp.create_load(net, bus=b14, name=2120754633, p_mw=0.001)

    # Le a haromfazisuakhoz
    b15 = pp.create_bus(net, vn_kv=0.4, name=15)
    l7 = pp.create_line(net, from_bus=b13, to_bus=b15, length_km=0.1995, std_type="4x150_Al_kbl", name='13_15')
    pp.create_switch(net, bus=b13, element=l7, et='l', type='CB', name='B7')
    pp.create_load(net, bus=b15, name=1079867888, p_mw=0.001)
    pp.create_load(net, bus=b15, name=1080271116, p_mw=0.001)
    pp.create_load(net, bus=b15, name=1079873304, p_mw=0.001)
    pp.create_load(net, bus=b15, name=2120755031, p_mw=0.001)
    pp.create_load(net, bus=b15, name=2120754812, p_mw=0.001)
    pp.create_load(net, bus=b15, name=2120754733, p_mw=0.001)
    pp.create_load(net, bus=b15, name=2120754742, p_mw=0.001)

    # B4
    b16 = pp.create_bus(net, vn_kv=0.4, name=16)
    pp.create_switch(net, bus=trafo_lv_side, element=b16, et='b', type='CB', name='B4')
    pp.create_load(net, bus=b16, name=2120755839, p_mw=0.001)
    b17 = pp.create_bus(net, vn_kv=0.4, name=17)
    pp.create_line(net, from_bus=b16, to_bus=b17, length_km=0.0206, std_type="4x50 Al", name='16_17')
    pp.create_load(net, bus=b17, name=2120756931, p_mw=0.001)
    pp.create_load(net, bus=b17, name=2120756653, p_mw=0.001)
    b18 = pp.create_bus(net, vn_kv=0.4, name=18)
    pp.create_line(net, from_bus=b17, to_bus=b18, length_km=0.0308, std_type="4x50 Al", name='17_18')
    pp.create_load(net, bus=b18, name=2120756540, p_mw=0.001)
    b19 = pp.create_bus(net, vn_kv=0.4, name=19)
    pp.create_line(net, from_bus=b18, to_bus=b19, length_km=0.0356, std_type="4x50 Al", name='18_19')
    '''HIANYZIK 25'''
    b20 = pp.create_bus(net, vn_kv=0.4, name=20)
    pp.create_line(net, from_bus=b19, to_bus=b20, length_km=0.0338, std_type="4x50 Al", name='19_20')
    pp.create_load(net, bus=b20, name=2120757088, p_mw=0.001)
    pp.create_load(net, bus=b20, name=2120756772, p_mw=0.001)
    pp.create_load(net, bus=b20, name=2120756720, p_mw=0.001)
    pp.create_load(net, bus=b20, name=2120756311, p_mw=0.001)
    b21 = pp.create_bus(net, vn_kv=0.4, name=21)
    pp.create_line(net, from_bus=b20, to_bus=b21, length_km=0.0363, std_type="4x50 Al", name='20_21')
    pp.create_load(net, bus=b21, name=2120755573, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2120755648, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2120754806, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2120755057, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2120756212, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2120754798, p_mw=0.001)
    b22 = pp.create_bus(net, vn_kv=0.4, name=22)
    pp.create_line(net, from_bus=b21, to_bus=b22, length_km=0.0311, std_type="4x50 Al", name='21_22')
    pp.create_load(net, bus=b22, name=2120756627, p_mw=0.001)
    pp.create_load(net, bus=b22, name=2120754957, p_mw=0.001)
    pp.create_load(net, bus=b22, name=2120755175, p_mw=0.001)
    pp.create_load(net, bus=b22, name=2120754415, p_mw=0.001)
    b23 = pp.create_bus(net, vn_kv=0.4, name=23)
    pp.create_line(net, from_bus=b22, to_bus=b23, length_km=0.0298, std_type="4x50 Al", name='22_23')
    pp.create_load(net, bus=b23, name=2120755701, p_mw=0.001)
    pp.create_load(net, bus=b23, name=2120756258, p_mw=0.001)
    pp.create_load(net, bus=b23, name=2120756253, p_mw=0.001)
    b24 = pp.create_bus(net, vn_kv=0.4, name=24)
    pp.create_line(net, from_bus=b23, to_bus=b24, length_km=0.0308, std_type="4x50 Al", name='23_24')
    pp.create_load(net, bus=b24, name=2120755270, p_mw=0.001)
    pp.create_load(net, bus=b24, name=2120755842, p_mw=0.001)
    pp.create_load(net, bus=b24, name=2120756397, p_mw=0.001)
    pp.create_load(net, bus=b24, name=2120757109, p_mw=0.001)
    pp.create_load(net, bus=b24, name=2120756400, p_mw=0.001)
    b25 = pp.create_bus(net, vn_kv=0.4, name=25)
    pp.create_line(net, from_bus=b24, to_bus=b25, length_km=0.0295, std_type="4x50 Al", name='24_25')
    pp.create_load(net, bus=b25, name=2120756798, p_mw=0.001)
    pp.create_load(net, bus=b25, name=2120754994, p_mw=0.001)
    b26 = pp.create_bus(net, vn_kv=0.4, name=26)
    pp.create_line(net, from_bus=b25, to_bus=b26, length_km=0.0335, std_type="4x50 Al", name='25_26')

    # B3
    b27 = pp.create_bus(net, vn_kv=0.4, name=27)
    pp.create_switch(net, bus=trafo_lv_side, element=b27, et='b', type='CB', name='B3')
    b28 = pp.create_bus(net, vn_kv=0.4, name=28)
    pp.create_line(net, from_bus=b27, to_bus=b28, length_km=0.015, std_type="4x95 Ml", name='27_28')
    b29 = pp.create_bus(net, vn_kv=0.4, name=29)
    pp.create_line(net, from_bus=b28, to_bus=b29, length_km=0.0216, std_type="4x95 Ml", name='28_29')
    b30 = pp.create_bus(net, vn_kv=0.4, name=30)
    pp.create_line(net, from_bus=b29, to_bus=b30, length_km=0.0386, std_type="4x95 Ml", name='29_30')

    # Leagazas ket fogyasztohoz
    b31 = pp.create_bus(net, vn_kv=0.4, name=31)
    pp.create_line(net, from_bus=b30, to_bus=b31, length_km=0.023, std_type="4x95 Ml", name='30_31')
    pp.create_load(net, bus=b31, name=2120754984, p_mw=0.001)
    pp.create_load(net, bus=b31, name=2120757002, p_mw=0.001)
    pp.create_load(net, bus=b31, name=2120756670, p_mw=0.001)
    pp.create_load(net, bus=b31, name=2120756683, p_mw=0.001)

    # Folytatas lefele balra be
    b32 = pp.create_bus(net, vn_kv=0.4, name=32)
    pp.create_line(net, from_bus=b30, to_bus=b32, length_km=0.0411, std_type="4x95 Ml", name='30_32')
    b33 = pp.create_bus(net, vn_kv=0.4, name=33)
    pp.create_line(net, from_bus=b32, to_bus=b33, length_km=0.033, std_type="4x95 Ml", name='32_33')
    pp.create_load(net, bus=b33, name=2120755240, p_mw=0.001)
    pp.create_load(net, bus=b33, name=2120756830, p_mw=0.001)
    pp.create_load(net, bus=b33, name=2120755037, p_mw=0.001)
    pp.create_load(net, bus=b33, name=2120755811, p_mw=0.001)
    pp.create_load(net, bus=b33, name=2120754836, p_mw=0.001)

    # Lefele tovabb
    b34 = pp.create_bus(net, vn_kv=0.4, name=34)
    pp.create_line(net, from_bus=b33, to_bus=b34, length_km=0.0361, std_type="4x50_Al_kbl", name='33_34')
    pp.create_load(net, bus=b34, name=2120756861, p_mw=0.001)
    b35 = pp.create_bus(net, vn_kv=0.4, name=35)
    pp.create_line(net, from_bus=b34, to_bus=b35, length_km=0.0441, std_type="4x50_Al_kbl", name='34_35')
    pp.create_load(net, bus=b35, name=2120755662, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2120756959, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2120755487, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2120756273, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2124380037, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2120755329, p_mw=0.001)

    # b33-rol folytatva balra
    b36 = pp.create_bus(net, vn_kv=0.4, name=36)
    pp.create_line(net, from_bus=b33, to_bus=b36, length_km=0.0313, std_type="4x95 Ml", name='33_36')
    pp.create_load(net, bus=b36, name=2120756560, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2120756735, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2120756969, p_mw=0.001)

    # b36-rol be, felfele
    b44 = pp.create_bus(net, vn_kv=0.4, name=44)
    pp.create_line(net, from_bus=b36, to_bus=b44, length_km=0.0417, std_type="4x10_Al", name='36_44')
    b45 = pp.create_bus(net, vn_kv=0.4, name=45)
    pp.create_line(net, from_bus=b44, to_bus=b45, length_km=0.0413, std_type="4x10_Al", name='44_45')
    pp.create_load(net, bus=b45, name=2120754664, p_mw=0.001)
    pp.create_load(net, bus=b45, name=2120755420, p_mw=0.001)

    # b36-rol folytatva balra
    b37 = pp.create_bus(net, vn_kv=0.4, name=37)
    pp.create_line(net, from_bus=b36, to_bus=b37, length_km=0.0303, std_type="4x95 Ml", name='36_37')
    pp.create_load(net, bus=b37, name=2120754826, p_mw=0.001)
    pp.create_load(net, bus=b37, name=2120755907, p_mw=0.001)
    pp.create_load(net, bus=b37, name=2120756837, p_mw=0.001)
    pp.create_load(net, bus=b37, name=2120755312, p_mw=0.001)
    pp.create_load(net, bus=b37, name=2120756267, p_mw=0.001)
    b38 = pp.create_bus(net, vn_kv=0.4, name=38)
    pp.create_line(net, from_bus=b37, to_bus=b38, length_km=0.0301, std_type="4x95 Ml", name='37_38')
    pp.create_load(net, bus=b38, name=2120756847, p_mw=0.001)
    pp.create_load(net, bus=b38, name=2120757062, p_mw=0.001)
    pp.create_load(net, bus=b38, name=2120755873, p_mw=0.001)
    b39 = pp.create_bus(net, vn_kv=0.4, name=39)
    pp.create_line(net, from_bus=b38, to_bus=b39, length_km=0.0297, std_type="4x95 Ml", name='38_39')
    pp.create_load(net, bus=b39, name=2120756244, p_mw=0.001)
    pp.create_load(net, bus=b39, name=2120754487, p_mw=0.001)
    pp.create_load(net, bus=b39, name=2120754868, p_mw=0.001)
    pp.create_load(net, bus=b39, name=2120756468, p_mw=0.001)
    pp.create_load(net, bus=b39, name=1042003967, p_mw=0.001)
    b40 = pp.create_bus(net, vn_kv=0.4, name=40)
    pp.create_line(net, from_bus=b39, to_bus=b40, length_km=0.031, std_type="4x95 Ml", name='39_40')
    pp.create_load(net, bus=b40, name=2120755341, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2120755708, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2120756448, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2120754899, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2120756125, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2120755099, p_mw=0.001)
    b41 = pp.create_bus(net, vn_kv=0.4, name=41)
    pp.create_line(net, from_bus=b40, to_bus=b41, length_km=0.0313, std_type="4x95 Ml", name='40_41')
    pp.create_load(net, bus=b41, name=2120756758, p_mw=0.001)
    pp.create_load(net, bus=b41, name=2120755442, p_mw=0.001)
    '''SAP2-bol kimaradt'''
    pp.create_load(net, bus=b41, name=2120755706, p_mw=0.001)
    pp.create_load(net, bus=b41, name=2120756820, p_mw=0.001)
    b42 = pp.create_bus(net, vn_kv=0.4, name=42)
    pp.create_line(net, from_bus=b41, to_bus=b42, length_km=0.0326, std_type="4x95 Ml", name='41_42')
    pp.create_load(net, bus=b42, name=2120756913, p_mw=0.001)
    pp.create_load(net, bus=b42, name=2120755913, p_mw=0.001)
    pp.create_load(net, bus=b42, name=2120754640, p_mw=0.001)
    pp.create_load(net, bus=b42, name=2120755447, p_mw=0.001)
    pp.create_load(net, bus=b42, name=2120755707, p_mw=0.001)
    b43 = pp.create_bus(net, vn_kv=0.4, name=43)
    pp.create_line(net, from_bus=b42, to_bus=b43, length_km=0.0409, std_type="4x95 Ml", name='42_43')
    pp.create_load(net, bus=b43, name=2120755845, p_mw=0.001)

    # B2
    b46 = pp.create_bus(net, vn_kv=0.4, name=46)
    pp.create_switch(net, bus=trafo_lv_side, element=b46, et='b', type='CB', name='B2')
    b47 = pp.create_bus(net, vn_kv=0.4, name=47)
    pp.create_line(net, from_bus=b46, to_bus=b47, length_km=0.015, std_type="4x95 Ml", name='46_47')
    b48 = pp.create_bus(net, vn_kv=0.4, name=48)
    pp.create_line(net, from_bus=b47, to_bus=b48, length_km=0.0216, std_type="4x95 Ml", name='47_48')
    pp.create_load(net, bus=b48, name=2120754535, p_mw=0.001)
    pp.create_load(net, bus=b48, name=2120754680, p_mw=0.001)
    pp.create_load(net, bus=b48, name=2120754866, p_mw=0.001)
    b49 = pp.create_bus(net, vn_kv=0.4, name=49)
    pp.create_line(net, from_bus=b48, to_bus=b49, length_km=0.0386, std_type="4x95 Al", name='48_49')
    b50 = pp.create_bus(net, vn_kv=0.4, name=50)
    pp.create_line(net, from_bus=b49, to_bus=b50, length_km=0.0411, std_type="4x95 Al", name='49_50')
    pp.create_load(net, bus=b50, name=2120756126, p_mw=0.001)

    # tovabb lefele
    b51 = pp.create_bus(net, vn_kv=0.4, name=51)
    pp.create_line(net, from_bus=b50, to_bus=b51, length_km=0.0425, std_type="4x95 Al", name='50_51')
    pp.create_load(net, bus=b51, name=2120755471, p_mw=0.001)
    pp.create_load(net, bus=b51, name=2120754683, p_mw=0.001)

    # el jobbra
    b52 = pp.create_bus(net, vn_kv=0.4, name=52)
    pp.create_line(net, from_bus=b50, to_bus=b52, length_km=0.0385, std_type="4x95 Al", name='50_52')
    pp.create_load(net, bus=b52, name=2120756249, p_mw=0.001)
    pp.create_load(net, bus=b52, name=2120755904, p_mw=0.001)
    b53 = pp.create_bus(net, vn_kv=0.4, name=53)
    pp.create_line(net, from_bus=b52, to_bus=b53, length_km=0.0386, std_type="4x95 Al", name='52_53')
    pp.create_load(net, bus=b53, name=2120755733, p_mw=0.001)
    pp.create_load(net, bus=b53, name=2120756605, p_mw=0.001)
    pp.create_load(net, bus=b53, name=2120755629, p_mw=0.001)

    # elindulas lefele
    b54 = pp.create_bus(net, vn_kv=0.4, name=54)
    pp.create_line(net, from_bus=b53, to_bus=b54, length_km=0.0399, std_type="4x95 Al", name='53_54')
    pp.create_load(net, bus=b54, name=2120757011, p_mw=0.001)
    pp.create_load(net, bus=b54, name=2120755320, p_mw=0.001)
    pp.create_load(net, bus=b54, name=2120754756, p_mw=0.001)
    pp.create_load(net, bus=b54, name=2120755296, p_mw=0.001)
    pp.create_load(net, bus=b54, name=2120755910, p_mw=0.001)
    b55 = pp.create_bus(net, vn_kv=0.4, name=55)
    pp.create_line(net, from_bus=b54, to_bus=b55, length_km=0.0418, std_type="4x95 Al", name='54_55')
    pp.create_load(net, bus=b55, name=2120755399, p_mw=0.001)
    pp.create_load(net, bus=b55, name=2120755570, p_mw=0.001)
    b56 = pp.create_bus(net, vn_kv=0.4, name=56)
    pp.create_line(net, from_bus=b55, to_bus=b56, length_km=0.0187, std_type="4x95 Ml", name='55_56')
    pp.create_load(net, bus=b56, name=2120755337, p_mw=0.001)
    pp.create_load(net, bus=b56, name=2120755773, p_mw=0.001)

    # el balra
    b57 = pp.create_bus(net, vn_kv=0.4, name=57)
    pp.create_line(net, from_bus=b56, to_bus=b57, length_km=0.034, std_type="4x50 Al", name='56_57')
    pp.create_load(net, bus=b57, name=2120754972, p_mw=0.001)
    pp.create_load(net, bus=b57, name=2120754677, p_mw=0.001)
    b58 = pp.create_bus(net, vn_kv=0.4, name=58)
    pp.create_line(net, from_bus=b57, to_bus=b58, length_km=0.0324, std_type="4x50 Al", name='57_58')
    pp.create_load(net, bus=b58, name=2120756800, p_mw=0.001)
    pp.create_load(net, bus=b58, name=2120755230, p_mw=0.001)

    # el jobbra
    b59 = pp.create_bus(net, vn_kv=0.4, name=59)
    pp.create_line(net, from_bus=b56, to_bus=b59, length_km=0.0313, std_type="4x50 Al", name='56_59')
    pp.create_load(net, bus=b59, name=2120755032, p_mw=0.001)
    pp.create_load(net, bus=b59, name=2120754627, p_mw=0.001)
    b60 = pp.create_bus(net, vn_kv=0.4, name=60)
    pp.create_line(net, from_bus=b59, to_bus=b60, length_km=0.0327, std_type="4x50 Al", name='59_60')
    pp.create_load(net, bus=b60, name=2120755982, p_mw=0.001)
    b61 = pp.create_bus(net, vn_kv=0.4, name=61)
    pp.create_line(net, from_bus=b60, to_bus=b61, length_km=0.0337, std_type="4x50 Al", name='60_61')
    pp.create_load(net, bus=b61, name=2120756439, p_mw=0.001)
    pp.create_load(net, bus=b61, name=2120755112, p_mw=0.001)
    b62 = pp.create_bus(net, vn_kv=0.4, name=62)
    pp.create_line(net, from_bus=b61, to_bus=b62, length_km=0.0332, std_type="4x50 Al", name='61_62')
    pp.create_load(net, bus=b62, name=2120754657, p_mw=0.001)
    pp.create_load(net, bus=b62, name=2120755289, p_mw=0.001)
    b63 = pp.create_bus(net, vn_kv=0.4, name=63)
    pp.create_line(net, from_bus=b62, to_bus=b63, length_km=0.0362, std_type="4x50 Al", name='62_63')
    pp.create_load(net, bus=b63, name=2120756170, p_mw=0.001)
    pp.create_load(net, bus=b63, name=2120756563, p_mw=0.001)
    b64 = pp.create_bus(net, vn_kv=0.4, name=64)
    pp.create_line(net, from_bus=b63, to_bus=b64, length_km=0.0266, std_type="4x25_ML", name='63_64')
    pp.create_load(net, bus=b64, name=2120755463, p_mw=0.001)
    pp.create_load(net, bus=b64, name=2120754988, p_mw=0.001)

    # b53-rol tovabb jobbra
    b65 = pp.create_bus(net, vn_kv=0.4, name=65)
    pp.create_line(net, from_bus=b53, to_bus=b65, length_km=0.0358, std_type="4x95 Al", name='53_65')
    pp.create_load(net, bus=b65, name=2120755788, p_mw=0.001)
    pp.create_load(net, bus=b65, name=2120755476, p_mw=0.001)
    pp.create_load(net, bus=b65, name=2120757036, p_mw=0.001)
    b66 = pp.create_bus(net, vn_kv=0.4, name=66)
    pp.create_line(net, from_bus=b65, to_bus=b66, length_km=0.0353, std_type="4x95 Al", name='65_66')
    pp.create_load(net, bus=b66, name=2120755816, p_mw=0.001)
    pp.create_load(net, bus=b66, name=2120756261, p_mw=0.001)

    # lefele
    b67 = pp.create_bus(net, vn_kv=0.4, name=67)
    pp.create_line(net, from_bus=b66, to_bus=b67, length_km=0.0349, std_type="4x50 Al", name='66_67')
    pp.create_load(net, bus=b67, name=2120756198, p_mw=0.001)
    pp.create_load(net, bus=b67, name=2120754453, p_mw=0.001)
    pp.create_load(net, bus=b67, name=2120755041, p_mw=0.001)
    b68 = pp.create_bus(net, vn_kv=0.4, name=68)
    pp.create_line(net, from_bus=b67, to_bus=b68, length_km=0.0329, std_type="4x50 Al", name='67_68')
    pp.create_load(net, bus=b68, name=2120756278, p_mw=0.001)

    # folytatas b66-rol
    b69 = pp.create_bus(net, vn_kv=0.4, name=69)
    pp.create_line(net, from_bus=b66, to_bus=b69, length_km=0.0293, std_type="4x95 Al", name='66_69')
    pp.create_load(net, bus=b69, name=2120755351, p_mw=0.001)
    pp.create_load(net, bus=b69, name=2120756066, p_mw=0.001)
    b70 = pp.create_bus(net, vn_kv=0.4, name=70)
    pp.create_line(net, from_bus=b69, to_bus=b70, length_km=0.0299, std_type="4x95 Al", name='69_70')
    pp.create_load(net, bus=b70, name=2120756502, p_mw=0.001)
    b71 = pp.create_bus(net, vn_kv=0.4, name=71)
    pp.create_line(net, from_bus=b70, to_bus=b71, length_km=0.0263, std_type="4x95 Al", name='70_71')
    pp.create_load(net, bus=b71, name=2120756929, p_mw=0.001)
    pp.create_load(net, bus=b71, name=2120754462, p_mw=0.001)
    pp.create_load(net, bus=b71, name=2120755828, p_mw=0.001)

    # lefele
    b72 = pp.create_bus(net, vn_kv=0.4, name=72)
    pp.create_line(net, from_bus=b71, to_bus=b72, length_km=0.0401, std_type="4x50 Al", name='71_72')
    pp.create_load(net, bus=b72, name=2120756651, p_mw=0.001)
    pp.create_load(net, bus=b72, name=2120755397, p_mw=0.001)
    pp.create_load(net, bus=b72, name=2120754835, p_mw=0.001)

    # folytatas felfele b71-rol
    b73 = pp.create_bus(net, vn_kv=0.4, name=73)
    pp.create_line(net, from_bus=b71, to_bus=b73, length_km=0.0394, std_type="4x50 Al", name='71_73')
    pp.create_load(net, bus=b73, name=2120754651, p_mw=0.001)
    pp.create_load(net, bus=b73, name=2120755803, p_mw=0.001)
    pp.create_load(net, bus=b73, name=2120755985, p_mw=0.001)
    b74 = pp.create_bus(net, vn_kv=0.4, name=74)
    pp.create_line(net, from_bus=b73, to_bus=b74, length_km=0.0390, std_type="4x50 Al", name='73_74')
    pp.create_load(net, bus=b74, name=2120757092, p_mw=0.001)
    pp.create_load(net, bus=b74, name=2120754848, p_mw=0.001)
    pp.create_load(net, bus=b74, name=2120755146, p_mw=0.001)
    pp.create_load(net, bus=b74, name=2120754935, p_mw=0.001)
    pp.create_load(net, bus=b74, name=2120754962, p_mw=0.001)

    # print network and run power flow
    pp.add_zero_impedance_parameters(net)
    # in case of run:
    if configuration.config.getboolean("network", "print_results"):
        print(net.line)
        print(net.bus)
        print(net.trafo)
        pp.runpp(net, calculate_voltage_angles=True, init='auto', max_iteration='auto', tolerance_mva=1e-08,
                 enforce_q_lims=False, numba=True, recycle=None, check_connectivity=True, switch_rx_ratio=2.0,
                 delta_q=0, v_debug=False)
        print(net.res_bus.vm_pu)
        print(net.res_line.loading_percent)
    return net


def preprocess_network():
    return create(configuration.config.get("paths", "pilot_path"))


if __name__ == "__main__":
    net = create()
