import pandapower as pp


def add_sgen_at_ext_grid(net):
    pp.create_sgen(net, net.ext_grid.bus[0], 0)
