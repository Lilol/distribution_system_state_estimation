import pandapower as pp
import pandapower.control


def build():
    # A modellezésnél az oszlopokat egyenlő távolságra vettem fel.
    # A leágazás 1 rész közvetlenül a transzformátor kisfeszültségű oldalától a hatos fogyasztó oszlopáig tart.
    # A transzformátornál a többi utca fogyasztóit koncentráltan képeztem le a MÉF_fogyszám_adatok excel táblázat szerint.
    # A leágazás1 busok nem rajz szerinti sorrendben lettek számozva. A transzformátortól a leágazás vége felé haladva: b2,b0,b5,b3,b4,b6
    # Főleágazás busoknál a name-ben a rá csatlakozó loadokat adtam meg.

    net = pp.create_empty_network(f_hz=50.0)

    # trafo bus
    b1 = pp.create_bus(net, vn_kv=20, name="b1")
    b2 = pp.create_bus(net, vn_kv=0.4, name="b2")

    # external grid
    pp.create_ext_grid(net, b1, 1)

    # trafo
    trafo = pp.create_transformer(net, b1, b2, "0.4 MVA 20/0.4 kV")

    # koncentrált fogyasztók
    pp.create_load(net, b2, 0.01832)
    pp.create_load(net, b2, 0.025852)
    pp.create_load(net, b2, 0.0173154)
    pp.create_load(net, b2, 0.0057077, 0.0022831)

    # leágazás1 bus
    b0 = pp.create_bus(net, 0.4, "b0")  # légkábel fogyasztó
    b5 = pp.create_bus(net, vn_kv=0.4, name="b5")  # légkábel vége
    b3 = pp.create_bus(net, 0.4, "b3")  # oszlopok
    b4 = pp.create_bus(net, 0.4, "b4")
    b6 = pp.create_bus(net, vn_kv=0.4, name="b6")  # leágazás 1 vége

    # leágazás1:
    # légkábel
    pp.create_line_from_parameters(net, b2, b0, 0.016, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b0, b5, 0.016, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    # légvezeték
    pp.create_line_from_parameters(net, b5, b3, 0.030, 0.311, 0.34, c_nf_per_km=0, max_i_ka=0.260, name="Al")
    pp.create_line_from_parameters(net, b3, b4, 0.030, 0.311, 0.34, c_nf_per_km=0, max_i_ka=0.260, name="Al")
    pp.create_line_from_parameters(net, b4, b6, 0.030, 0.311, 0.34, c_nf_per_km=0, max_i_ka=0.260, name="Al")

    # leágazás1
    pp.create_load(net, b0, p_mw=0)
    pp.create_load(net, b3, p_mw=0)
    pp.create_load(net, b3, p_mw=0)
    pp.create_load(net, b4, p_mw=0)
    pp.create_load(net, b4, p_mw=0)
    pp.create_load(net, b6, p_mw=0)

    # főleágazás
    # bus
    b7 = pp.create_bus(net, 0.4, name="7-8")
    b8 = pp.create_bus(net, 0.4, name="9-10-11")
    b9 = pp.create_bus(net, 0.4, name="12-13")
    b10 = pp.create_bus(net, 0.4, name="14-15-16-17")
    b11 = pp.create_bus(net, 0.4, name="18-19-20-21-22")
    b12 = pp.create_bus(net, 0.4, name="23-24-25")
    b121 = pp.create_bus(net, 0.4, name="IVR2")
    b13 = pp.create_bus(net, 0.4, name="26-27-28-29")
    b14 = pp.create_bus(net, 0.4, name="30-31-32-33")
    b15 = pp.create_bus(net, 0.4, name="34-35-36-37-38")
    b16 = pp.create_bus(net, 0.4, name="39-40")
    b17 = pp.create_bus(net, 0.4, name="41")
    b18 = pp.create_bus(net, 0.4, name="42-43-44-45")
    b19 = pp.create_bus(net, 0.4, name="46-47-48-49")
    b20 = pp.create_bus(net, 0.4, name="50-51")
    b21 = pp.create_bus(net, 0.4, name="52")
    b22 = pp.create_bus(net, 0.4, name="53")

    # line
    pp.create_line_from_parameters(net, b6, b7, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b7, b8, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b8, b9, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b9, b10, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b10, b11, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b11, b12, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    # pp.create_line_from_parameters(net, b12, b121, 0.0001, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b121, b13, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b13, b14, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b14, b15, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b15, b16, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b16, b17, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b17, b18, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b18, b19, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b19, b20, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b20, b21, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")
    pp.create_line_from_parameters(net, b21, b22, 0.0328125, 0.311, 0.071, c_nf_per_km=0, max_i_ka=0.160, name="ML")

    # főleágazás fogyasztók
    pp.create_load(net, b7, p_mw=0)
    pp.create_load(net, b7, p_mw=0)  # 7-8

    pp.create_load(net, b8, p_mw=0)
    pp.create_load(net, b8, p_mw=0)
    pp.create_load(net, b8, p_mw=0)  # 9-10-11

    pp.create_load(net, b9, p_mw=0)
    pp.create_load(net, b9, p_mw=0)  # 12-13

    pp.create_load(net, b10, p_mw=0)
    pp.create_load(net, b10, p_mw=0)
    pp.create_load(net, b10, p_mw=0)
    pp.create_load(net, b10, p_mw=0)  # 14-17

    pp.create_load(net, b11, p_mw=0)
    pp.create_load(net, b11, p_mw=0)
    pp.create_load(net, b11, p_mw=0)
    pp.create_load(net, b11, p_mw=0)
    pp.create_load(net, b11, p_mw=0)  # 18-22

    pp.create_load(net, b12, p_mw=0)
    pp.create_load(net, b12, p_mw=0)
    pp.create_load(net, b12, p_mw=0)  # 23-25

    pp.create_load(net, b13, p_mw=0)
    pp.create_load(net, b13, p_mw=0)
    pp.create_load(net, b13, p_mw=0)
    pp.create_load(net, b13, p_mw=0)  # 26-29

    pp.create_load(net, b14, p_mw=0)
    pp.create_load(net, b14, p_mw=0)
    pp.create_load(net, b14, p_mw=0)
    pp.create_load(net, b14, p_mw=0)  # 30-33

    pp.create_load(net, b15, p_mw=0)
    pp.create_load(net, b15, p_mw=0)
    pp.create_load(net, b15, p_mw=0)
    pp.create_load(net, b15, p_mw=0)
    pp.create_load(net, b15, p_mw=0)  # 34-38

    pp.create_load(net, b16, p_mw=0)
    pp.create_load(net, b16, p_mw=0)  # 39-40

    pp.create_load(net, b17, p_mw=0)  # 41

    pp.create_load(net, b18, p_mw=0)
    pp.create_load(net, b18, p_mw=0)
    pp.create_load(net, b18, p_mw=0)
    pp.create_load(net, b18, p_mw=0)  # 42-45

    pp.create_load(net, b19, p_mw=0)
    pp.create_load(net, b19, p_mw=0)
    pp.create_load(net, b19, p_mw=0)
    pp.create_load(net, b19, p_mw=0)  # 46-49

    pp.create_load(net, b20, p_mw=0)
    pp.create_load(net, b20, p_mw=0)  # 50-51

    pp.create_load(net, b21, p_mw=0)  # 52

    pp.create_load(net, b21, p_mw=0)  # 53

    # IVR
    pp.create_transformer_from_parameters(net, hv_bus=b12, lv_bus=b121, sn_mva=0.25, vn_hv_kv=0.4, vn_lv_kv=0.4,
                                          vk_percent=2, vkr_percent=0.3, pfe_kw=1.5, i0_percent=1, tap_pos=0,
                                          tap_side="lv", tap_neutral=0, tap_min=-9, tap_max=9, oltc=True,
                                          tap_step_percent=0.5)
    pandapower.control.ContinuousTapControl(net, 1, 1, 0.01, side="lv", in_service=True)

    net.load.name = net.load.index.astype("str")
    net.load.const_z_percent = 1.
    net.line.name = net.line.index.astype("str")
    net.bus.name = net.bus.index.astype("str")

    return net
