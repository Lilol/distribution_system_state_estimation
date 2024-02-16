def add(net, nodes, conns, devs, assists, trs):
    net.trafo['area'] = None
    # for loop on trafos. The last is the HV/MV so it is not needed
    for i in net.trafo.index.tolist()[:-1]:
        net.trafo.at[i, 'area'] = trs[trs['FID'] == net.trafo.at[i, 'name']]['Állomás szám '].mode().iloc[0]
    net.bus['area'] = None
    # buses
    for i in net.bus.index.tolist():
        name = net.bus.at[i, 'name']
        if type(name) == str and 'node' in name:
            net.bus.at[i, 'area'] = nodes[nodes['FID'] == int(name.split('_')[1])]['Állomás szám '].mode().iloc[0]

    net.switch['area'] = None
    # switches
    for i in net.switch.index.tolist():
        name = net.switch.at[i, 'name']
        if 'conn' in name:
            net.switch.at[i, 'area'] = \
                conns[conns['FID'] == int(name.split('_')[1])]['Azonosító Ele Kapcsoló berendezés hely '].iloc[0]
        elif 'dev' in name:
            net.switch.at[i, 'area'] = devs[devs['FID'] == int(name.split('_')[1])]['Állomás szám '].mode().iloc[0]
        else:
            pass
    net.switch['area'] = net.switch['area'].fillna(0)  # .astype(int)

    # assists
    net.line['area'] = None
    for i in net.line.index.tolist():
        name = net.line.at[i, 'name']
        if type(name) == str and 'assist' in name:
            net.line.at[i, 'area'] = assists[assists['FID'] == int(name.split('_')[1])]['Állomás szám '].iloc[0]
    net.line['area'] = net.line['area'].fillna(0).astype(int)
