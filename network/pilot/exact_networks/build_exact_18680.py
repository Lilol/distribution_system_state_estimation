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
                  'vk_percent': 4.665, 'vkr_percent': 1.8,
                  'vk0_percent': 4.665, 'vkr0_percent': 1.8,
                  'sn_mva': 0.16, 'i0_percent': 3,
                  'vector_group': 'Dyn5', "shift_degree": 150,
                  'pfe_kw': 0.43}

    # create type for the trafo
    pp.create_std_type(net, trafo_data, name='IE 35-116', element='trafo')
    trafo_mv_side = pp.create_bus(net, vn_kv=21, name="Trafo MV")
    trafo_lv_side = pp.create_bus(net, vn_kv=0.4, name="Trafo LV")
    # Create bus for external grid
    bus0 = pp.create_bus(net, vn_kv=21, name="Ext grid")
    pp.create_transformer(net, hv_bus=trafo_mv_side, lv_bus=trafo_lv_side, std_type='IE 35-116')
    # Create external grid and switch
    pp.create_ext_grid(net, bus=bus0)
    pp.create_switch(net, bus=bus0, element=trafo_mv_side, et='b', closed=True, type='CB', name='S1')

    _4x95Al = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.34, "c_nf_per_km": 0, "max_i_ka": 0.25, "r0_ohm_per_km": 1.244,
               "x0_ohm_per_km": 1.36, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Al, name="4x95 Al", element="line")
    _4x95Ml = {"r_ohm_per_km": 0.311, "x_ohm_per_km": 0.071, "c_nf_per_km": 0, "max_i_ka": 0.16, "r0_ohm_per_km": 1.244,
               "x0_ohm_per_km": 0.284, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x95Ml, name="4x95 Ml", element="line")
    _4x50Al = {"r_ohm_per_km": 0.603, "x_ohm_per_km": 0.357, "c_nf_per_km": 0, "max_i_ka": 0.16, "r0_ohm_per_km": 2.412,
               "x0_ohm_per_km": 1.428, "c0_nf_per_km": 0}
    pp.create_std_type(net, _4x50Al, name="4x50 Al", element="line")

    # Meggyfa utca jobb oldala
    b1 = pp.create_bus(net, vn_kv=0.4, name=1)
    l2 = pp.create_line(net, from_bus=trafo_lv_side, to_bus=b1, length_km=0.0264, std_type="4x95 Ml",
                        name='trafo_lv_side_1')
    pp.create_switch(net, bus=trafo_lv_side, element=l2, et='l', type='CB', name='B2')
    b2 = pp.create_bus(net, vn_kv=0.4, name=2)
    pp.create_line(net, from_bus=b1, to_bus=b2, length_km=0.0302, std_type="4x95 Ml", name='1_2')
    pp.create_load(net, bus=b2, name=2125894580, p_mw=0.001)
    pp.create_load(net, bus=b2, name=2125895197, p_mw=0.001)
    b3 = pp.create_bus(net, vn_kv=0.4, name=3)
    pp.create_line(net, from_bus=b2, to_bus=b3, length_km=0.0357, std_type="4x95 Ml", name='2_3')
    pp.create_load(net, bus=b3, name=2125894438, p_mw=0.001)
    b4 = pp.create_bus(net, vn_kv=0.4, name=4)
    pp.create_line(net, from_bus=b3, to_bus=b4, length_km=0.0334, std_type="4x95 Ml", name='3_4')
    pp.create_load(net, bus=b4, name=1080233202, p_mw=0.001)
    b5 = pp.create_bus(net, vn_kv=0.4, name=5)
    pp.create_line(net, from_bus=b4, to_bus=b5, length_km=0.0196, std_type="4x95 Ml", name='4_5')
    pp.create_load(net, bus=b5, name=2125895136, p_mw=0.001)
    pp.create_load(net, bus=b5, name=2125894677, p_mw=0.001)

    # Meggyfa utca bal oldala és kiérve a Liget sorra balra fordulva
    b6 = pp.create_bus(net, vn_kv=0.4, name=6)
    l1 = pp.create_line(net, from_bus=trafo_lv_side, to_bus=b6, length_km=0.0264, std_type="4x95 Ml",
                        name='trafo_lv_side_6')
    pp.create_switch(net, bus=trafo_lv_side, element=l1, et='l', type='CB', name='B1')
    pp.create_load(net, bus=b6, name=2125893622, p_mw=0.001)
    b7 = pp.create_bus(net, vn_kv=0.4, name=7)
    pp.create_line(net, from_bus=b6, to_bus=b7, length_km=0.0302, std_type="4x95 Ml", name='6_7')
    pp.create_load(net, bus=b7, name=2125894113, p_mw=0.001)
    pp.create_load(net, bus=b7, name=2125893837, p_mw=0.001)
    b8 = pp.create_bus(net, vn_kv=0.4, name=8)
    pp.create_line(net, from_bus=b7, to_bus=b8, length_km=0.0357, std_type="4x95 Ml", name='7_8')
    pp.create_load(net, bus=b8, name=2125894126, p_mw=0.001)
    pp.create_load(net, bus=b8, name=2125893381, p_mw=0.001)
    b9 = pp.create_bus(net, vn_kv=0.4, name=9)
    pp.create_line(net, from_bus=b8, to_bus=b9, length_km=0.0334, std_type="4x95 Ml", name='8_9')
    pp.create_load(net, bus=b9, name=2125894357, p_mw=0.001)
    b10 = pp.create_bus(net, vn_kv=0.4, name=10)
    pp.create_line(net, from_bus=b9, to_bus=b10, length_km=0.0196, std_type="4x95 Ml", name='9_10')
    b11 = pp.create_bus(net, vn_kv=0.4, name=11)
    pp.create_line(net, from_bus=b10, to_bus=b11, length_km=0.0351, std_type="4x95 Ml", name='10_11')
    b12 = pp.create_bus(net, vn_kv=0.4, name=12)
    pp.create_line(net, from_bus=b11, to_bus=b12, length_km=0.0361, std_type="4x95 Ml", name='11_12')
    b13 = pp.create_bus(net, vn_kv=0.4, name=13)
    pp.create_line(net, from_bus=b12, to_bus=b13, length_km=0.0380, std_type="4x95 Ml", name='12_13')
    b14 = pp.create_bus(net, vn_kv=0.4, name=14)
    pp.create_line(net, from_bus=b13, to_bus=b14, length_km=0.0248, std_type="4x95 Ml", name='13_14')

    # Meggyfa utcáról kiérve jobbra a Liget sorra fordulva (b5 sínről folytatva)
    b15 = pp.create_bus(net, vn_kv=0.4, name=15)
    pp.create_line(net, from_bus=b5, to_bus=b15, length_km=0.0410, std_type="4x95 Al", name='5_15')
    pp.create_load(net, bus=b15, name=2125894251, p_mw=0.001)
    pp.create_load(net, bus=b15, name=1049734840, p_mw=0.001)
    pp.create_load(net, bus=b15, name=2125893678, p_mw=0.001)
    b16 = pp.create_bus(net, vn_kv=0.4, name=16)
    pp.create_line(net, from_bus=b15, to_bus=b16, length_km=0.0381, std_type="4x95 Al", name='15_16')
    pp.create_load(net, bus=b16, name=2125894440, p_mw=0.001)
    pp.create_load(net, bus=b16, name=2125893919, p_mw=0.001)
    b17 = pp.create_bus(net, vn_kv=0.4, name=17)
    pp.create_line(net, from_bus=b16, to_bus=b17, length_km=0.0204, std_type="4x95 Al", name='16_17')

    # A Ligetsorról (b17-ről) be az Iparos közbe
    b18 = pp.create_bus(net, vn_kv=0.4, name=18)
    l5 = pp.create_line(net, from_bus=b17, to_bus=b18, length_km=0.0323, std_type="4x50 Al", name='17_18')
    pp.create_switch(net, bus=b17, element=l5, et='l', type='CB', name='B5')
    pp.create_load(net, bus=b18, name=2125894595, p_mw=0.001)
    pp.create_load(net, bus=b18, name=2125895169, p_mw=0.001)
    b19 = pp.create_bus(net, vn_kv=0.4, name=19)
    pp.create_line(net, from_bus=b18, to_bus=b19, length_km=0.0299, std_type="4x50 Al", name='18_19')
    pp.create_load(net, bus=b19, name=2125895244, p_mw=0.001)
    pp.create_load(net, bus=b19, name=2125893600, p_mw=0.001)
    b20 = pp.create_bus(net, vn_kv=0.4, name=20)
    pp.create_line(net, from_bus=b19, to_bus=b20, length_km=0.0284, std_type="4x50 Al", name='19_20')

    # Tovább haladva a Liget sor végéig a már elért b17-től
    b21 = pp.create_bus(net, vn_kv=0.4, name=21)
    pp.create_line(net, from_bus=b17, to_bus=b21, length_km=0.0166, std_type="4x95 Al", name='17_21')
    pp.create_load(net, bus=b21, name=2125893726, p_mw=0.001)
    pp.create_load(net, bus=b21, name=2125895151, p_mw=0.001)
    b22 = pp.create_bus(net, vn_kv=0.4, name=22)
    pp.create_line(net, from_bus=b21, to_bus=b22, length_km=0.0372, std_type="4x95 Al", name='21_22')
    pp.create_load(net, bus=b22, name=2125894827, p_mw=0.001)
    pp.create_load(net, bus=b22, name=2125894681, p_mw=0.001)
    b23 = pp.create_bus(net, vn_kv=0.4, name=23)
    pp.create_line(net, from_bus=b22, to_bus=b23, length_km=0.0385, std_type="4x95 Al", name='22_23')
    pp.create_load(net, bus=b23, name=2125895085, p_mw=0.001)
    b24 = pp.create_bus(net, vn_kv=0.4, name=24)
    pp.create_line(net, from_bus=b23, to_bus=b24, length_km=0.0322, std_type="4x95 Al", name='23_24')
    pp.create_load(net, bus=b24, name=2125894048, p_mw=0.001)

    # Folytatva arról a vezetékről ami a Meggyfa utca bal oldaláról jött és a Liget soron
    # balra fordult. Tehát a Liget sor b14-ről be a Patak utcába
    b25 = pp.create_bus(net, vn_kv=0.4, name=25)
    l3 = pp.create_line(net, from_bus=b14, to_bus=b25, length_km=0.0178, std_type="4x95 Al", name='14_25')
    pp.create_switch(net, bus=b14, element=l3, et='l', type='CB', name='B3')
    pp.create_load(net, bus=b25, name=2125895152, p_mw=0.001)
    pp.create_load(net, bus=b25, name=2125893884, p_mw=0.001)
    b26 = pp.create_bus(net, vn_kv=0.4, name=26)
    pp.create_line(net, from_bus=b25, to_bus=b26, length_km=0.0379, std_type="4x95 Al", name='25_26')
    pp.create_load(net, bus=b26, name=2125893532, p_mw=0.001)
    pp.create_load(net, bus=b26, name=2125894636, p_mw=0.001)
    pp.create_load(net, bus=b26, name=2125893820, p_mw=0.001)
    pp.create_load(net, bus=b26, name=2125894788, p_mw=0.001)
    b27 = pp.create_bus(net, vn_kv=0.4, name=27)
    pp.create_line(net, from_bus=b26, to_bus=b27, length_km=0.0383, std_type="4x95 Al", name='26_27')
    pp.create_load(net, bus=b27, name=2125895256, p_mw=0.001)
    pp.create_load(net, bus=b27, name=2125894823, p_mw=0.001)
    pp.create_load(net, bus=b27, name=2125894709, p_mw=0.001)
    pp.create_load(net, bus=b27, name=2125893505, p_mw=0.001)
    b28 = pp.create_bus(net, vn_kv=0.4, name=28)
    pp.create_line(net, from_bus=b27, to_bus=b28, length_km=0.0378, std_type="4x95 Al", name='27_28')
    pp.create_load(net, bus=b28, name=2125895211, p_mw=0.001)
    pp.create_load(net, bus=b28, name=1049738980, p_mw=0.001)
    pp.create_load(net, bus=b28, name=2125894924, p_mw=0.001)

    # b14-ről tovább a Liget soron egészen a Hűvösvölgyi utcáig
    b29 = pp.create_bus(net, vn_kv=0.4, name=29)
    pp.create_line(net, from_bus=b14, to_bus=b29, length_km=0.0109, std_type="4x95 Ml", name='14_29')
    b30 = pp.create_bus(net, vn_kv=0.4, name=30)
    pp.create_line(net, from_bus=b29, to_bus=b30, length_km=0.0361, std_type="4x95 Ml", name='29_30')
    b31 = pp.create_bus(net, vn_kv=0.4, name=31)
    pp.create_line(net, from_bus=b30, to_bus=b31, length_km=0.0405, std_type="4x95 Ml", name='30_31')
    b32 = pp.create_bus(net, vn_kv=0.4, name=32)
    pp.create_line(net, from_bus=b31, to_bus=b32, length_km=0.0379, std_type="4x95 Ml", name='31_32')
    b33 = pp.create_bus(net, vn_kv=0.4, name=33)
    pp.create_line(net, from_bus=b32, to_bus=b33, length_km=0.0103, std_type="4x95 Ml", name='32_33')

    # Be a Hűvösvölgyi utcába a Liget sorról (b33-ról)
    b34 = pp.create_bus(net, vn_kv=0.4, name=34)
    l4 = pp.create_line(net, from_bus=b33, to_bus=b34, length_km=0.0171, std_type="4x95 Al", name='33_34')
    pp.create_switch(net, bus=b33, element=l4, et='l', type='CB', name='B4')
    pp.create_load(net, bus=b34, name=2125895069, p_mw=0.001)
    b35 = pp.create_bus(net, vn_kv=0.4, name=35)
    pp.create_line(net, from_bus=b34, to_bus=b35, length_km=0.0336, std_type="4x95 Al", name='34_35')
    pp.create_load(net, bus=b35, name=2125894717, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2125895062, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2125894898, p_mw=0.001)
    pp.create_load(net, bus=b35, name=2125894258, p_mw=0.001)
    b36 = pp.create_bus(net, vn_kv=0.4, name=36)
    pp.create_line(net, from_bus=b35, to_bus=b36, length_km=0.0347, std_type="4x95 Al", name='35_36')
    pp.create_load(net, bus=b36, name=2125894092, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2125894770, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2125895198, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2125894578, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2125894564, p_mw=0.001)
    pp.create_load(net, bus=b36, name=2125893918, p_mw=0.001)

    # El a Liget sor baloldali vezetékének végéig (b33-ról)
    b37 = pp.create_bus(net, vn_kv=0.4, name=37)
    pp.create_line(net, from_bus=b33, to_bus=b37, length_km=0.0219, std_type="4x95 Ml", name='33_37')

    # Folytatva arról a vezetérkről ami a Meggyfa utca jobb oldaláról jött ki (b5-ről folytatva)
    # A Liget soron balra fordulva, elmenve a legvégéig
    b38 = pp.create_bus(net, vn_kv=0.4, name=38)
    pp.create_line(net, from_bus=b5, to_bus=b38, length_km=0.0351, std_type="4x95 Al", name='5_38')
    pp.create_load(net, bus=b38, name=2125894271, p_mw=0.001)
    pp.create_load(net, bus=b38, name=2125895122, p_mw=0.001)
    pp.create_load(net, bus=b38, name=2125893888, p_mw=0.001)
    b39 = pp.create_bus(net, vn_kv=0.4, name=39)
    pp.create_line(net, from_bus=b38, to_bus=b39, length_km=0.0361, std_type="4x95 Al", name='38_39')
    pp.create_load(net, bus=b39, name=2125895210, p_mw=0.001)
    b40 = pp.create_bus(net, vn_kv=0.4, name=40)
    pp.create_line(net, from_bus=b39, to_bus=b40, length_km=0.0380, std_type="4x95 Al", name='39_40')
    pp.create_load(net, bus=b40, name=2125894238, p_mw=0.001)
    pp.create_load(net, bus=b40, name=2125893410, p_mw=0.001)
    b41 = pp.create_bus(net, vn_kv=0.4, name=41)
    pp.create_line(net, from_bus=b40, to_bus=b41, length_km=0.0248, std_type="4x95 Al", name='40_41')
    b42 = pp.create_bus(net, vn_kv=0.4, name=42)
    pp.create_line(net, from_bus=b41, to_bus=b42, length_km=0.0109, std_type="4x95 Al", name='41_42')
    pp.create_load(net, bus=b42, name=2125895240, p_mw=0.001)
    b43 = pp.create_bus(net, vn_kv=0.4, name=43)
    pp.create_line(net, from_bus=b42, to_bus=b43, length_km=0.0361, std_type="4x95 Al", name='42_43')
    pp.create_load(net, bus=b43, name=2125893970, p_mw=0.001)
    pp.create_load(net, bus=b43, name=2125893893, p_mw=0.001)
    b44 = pp.create_bus(net, vn_kv=0.4, name=44)
    pp.create_line(net, from_bus=b43, to_bus=b44, length_km=0.0405, std_type="4x95 Al", name='43_44')
    pp.create_load(net, bus=b44, name=2125894655, p_mw=0.001)
    pp.create_load(net, bus=b44, name=2125893523, p_mw=0.001)
    b45 = pp.create_bus(net, vn_kv=0.4, name=45)
    pp.create_line(net, from_bus=b44, to_bus=b45, length_km=0.0379, std_type="4x95 Al", name='44_45')
    pp.create_load(net, bus=b45, name=2125893556, p_mw=0.001)
    b46 = pp.create_bus(net, vn_kv=0.4, name=46)
    pp.create_line(net, from_bus=b45, to_bus=b46, length_km=0.0103, std_type="4x95 Al", name='45_46')
    b47 = pp.create_bus(net, vn_kv=0.4, name=47)
    pp.create_line(net, from_bus=b46, to_bus=b47, length_km=0.0219, std_type="4x95 Al", name='46_47')
    pp.create_load(net, bus=b47, name=2125893628, p_mw=0.001)
    pp.create_load(net, bus=b47, name=2125894078, p_mw=0.001)
    b48 = pp.create_bus(net, vn_kv=0.4, name=48)
    pp.create_line(net, from_bus=b47, to_bus=b48, length_km=0.0383, std_type="4x95 Al", name='47_48')
    pp.create_load(net, bus=b48, name=2125894630, p_mw=0.001)
    pp.create_load(net, bus=b48, name=2125894722, p_mw=0.001)
    pp.create_load(net, bus=b48, name=2125893503, p_mw=0.001)
    b49 = pp.create_bus(net, vn_kv=0.4, name=49)
    pp.create_line(net, from_bus=b48, to_bus=b49, length_km=0.0357, std_type="4x95 Al", name='48_49')
    pp.create_load(net, bus=b49, name=2125894432, p_mw=0.001)
    pp.create_load(net, bus=b49, name=2125893561, p_mw=0.001)
    pp.create_load(net, bus=b49, name=2125894453, p_mw=0.001)
    pp.create_load(net, bus=b49, name=2125894348, p_mw=0.001)
    b50 = pp.create_bus(net, vn_kv=0.4, name=50)
    pp.create_line(net, from_bus=b49, to_bus=b50, length_km=0.0385, std_type="4x95 Al", name='49_50')
    pp.create_load(net, bus=b50, name=2125894896, p_mw=0.001)
    pp.create_load(net, bus=b50, name=2125893549, p_mw=0.001)
    pp.create_load(net, bus=b50, name=2125893522, p_mw=0.001)
    b51 = pp.create_bus(net, vn_kv=0.4, name=51)
    pp.create_line(net, from_bus=b50, to_bus=b51, length_km=0.0377, std_type="4x95 Al", name='50_51')
    pp.create_load(net, bus=b51, name=2125894363, p_mw=0.001)
    pp.create_load(net, bus=b51, name=2125895003, p_mw=0.001)
    b52 = pp.create_bus(net, vn_kv=0.4, name=52)
    pp.create_line(net, from_bus=b51, to_bus=b52, length_km=0.0364, std_type="4x95 Al", name='51_52')
    pp.create_load(net, bus=b52, name=2125894541, p_mw=0.001)
    pp.create_load(net, bus=b52, name=2125894883, p_mw=0.001)

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
    # Missing load:2125893445
