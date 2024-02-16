from datetime import timedelta
from glob import glob
from itertools import chain
from logging import getLogger
from os.path import join
from random import seed, SystemRandom
from time import strptime

import pandapower.topology as ppt
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import read_excel

import utility.configuration as configuration
from data_extractor.definitions import OutputMode, data_kind_to_quantity
from measurement.pilot.metering_device_position import to_sm_name
from network.definitions import NetworkId
from output_writer.assemble_path import assemble_path, assemble_file

search_for1 = ["tr_1842593_hv",
               "tr_1842593_lv",
               "assist_2121752979_8",
               "assist_2121752979_9",
               "dev_2121753760_2_second",
               "dev_2121753760_2",
               "assist_2121753421_2",
               "assist_2121753421_3",
               "line_2121755244_34",
               "line_2121755244_35",
               "line_1080152487_0",
               "line_1080152487_1",
               "line_1080152487_2",
               "line_1080152487_3",
               "line_2121754282_4",
               "line_2121754282_5",
               "dev_2121753746_0",
               "dev_2121753746_0_second",
               "line_2121752678_26",
               "line_2121752678_27",
               "line_2121752678_28",
               "line_2121752678_29",
               "line_2121752678_30"]

search_for2 = list(range(0, 24))


def get_search_for():
    return search_for1 if configuration.config.get_network_id() == NetworkId.ID_23427 else [str(s) for s in search_for2]


def display():
    search_for = get_search_for()
    output_path = assemble_path()
    output_file = assemble_file("network_params_difference", OutputMode.EXCEL)
    df = read_excel(join(output_path, output_file), sheet_name="node_voltage_pu", header=0, engine="openpyxl",
                    index_col=0)

    plt.figure(figsize=(10, 5))
    plt.plot(range(len(search_for)), list(df.loc["Root mean square", search_for]))
    plt.xlabel("Bus order from trafo")
    plt.ylabel("Error")
    plt.savefig(join(output_path, "parameter_difference.png"))


def display2():
    search_for = get_search_for()

    f, axes = plt.subplots(1, 2, figsize=(15, 4))
    path = join(configuration.config.get("paths", "measurement_path"), "network_params_simulation.xlsx")
    df = pd.read_excel(path, engine="openpyxl", sheet_name="node_voltage_pu")
    df = df[["Iteration"] + search_for]
    df.rename(columns={c: i for c, i in zip(df.columns[1:], range(len(df.columns[1:])))}, inplace=True)
    df_unpivot = pd.melt(df, id_vars='Iteration', value_vars=df.columns[1:])
    df_unpivot.variable = df_unpivot.variable.astype('int')
    sns.boxplot(df_unpivot, x="variable", y="value", ax=axes[0]).set(title="State estimation", ylim=[0.9, 1.09],
                                                                     xlabel="Distance from trafo", ylabel="U [p.u.]")

    path = join(configuration.config.get("paths", "measurement_path"), "network_params_validation.xlsx")
    df = pd.read_excel(path, engine="openpyxl", sheet_name="node_voltage_pu")
    df = df[["Iteration"] + search_for]
    df.rename(columns={c: i for c, i in zip(df.columns[1:], range(len(df.columns[1:])))}, inplace=True)
    df_unpivot = pd.melt(df, id_vars='Iteration', value_vars=df.columns[1:])
    df_unpivot.variable = df_unpivot.variable.astype('int')
    sns.boxplot(df_unpivot, x="variable", y="value", ax=axes[1]).set(title="Loadflow", ylim=[0.9, 1.09],
                                                                     xlabel="Distance from trafo", ylabel="U [p.u.]")
    plt.tight_layout()
    plt.savefig(join(configuration.config.get("paths", "measurement_path"), "voltage_variance.png"))


def read(scenario, data_type):
    path = join(configuration.config.get("paths", "output_path"),
                f"network_params_difference_sc{scenario.value}.xlsx")
    df = pd.read_excel(path, engine="openpyxl", sheet_name=data_type.value, header=0, index_col=0)
    df.rename(columns={c: to_sm_name(i, data_type) for c, i in zip(df.columns[1:], range(len(df.columns[1:])))},
              inplace=True)
    return df

def display_error_variance_by_pos_sm(data_type, relative=False, scenario=configuration.config.get_scenario()):
    df = read(scenario, data_type)
    df_unpivot = pd.melt(df, id_vars='Iteration', value_vars=df.columns[1:])
    df_unpivot.variable = df_unpivot.variable.astype('int')
    sns.boxplot(df_unpivot, x="variable", y="value").set(title="Error",
                                                         xlabel="Element",
                                                         ylabel=data_kind_to_quantity(data_type))

    plt.tight_layout()
    plt.savefig(join(configuration.config.get("paths", "measurement_path"), f"{data_type.value}_variance.png"))


def display_error_variance_by_time_sm(data_type, relative=False, scenario=configuration.config.get_scenario()):
    f, axes = plt.plot(figsize=(7, 4))
    df = read(scenario, data_type)
    df.Date = pd.to_datetime(
        strptime("2023-01-17 09:00:00", format="%Y-%m-%d %h:%M:%s") + timedelta(minutes=df.index * 15))
    df = df.set_index("Date")
    # df_unpivot = pd.melt(df, id_vars='Iteration', value_vars=df.columns[1:])
    # df_unpivot.variable = df_unpivot.variable.astype('int')
    sns.lineplot(df, x="variable", y="value", ax=axes[0]).set(title="Error",
                                                              xlabel="Time", ylabel=data_kind_to_quantity(data_type))

    plt.tight_layout()
    plt.savefig(join(configuration.config.get("paths", "measurement_path"), f"{data_type.value}_variance.png"))


def get_indices_from_names(net, names, element_type="bus"):
    indices = []
    try:
        if element_type == "bus":
            indices = [net.bus[net.bus.name.str.endswith(str(name))].index[0] for name in names]
        elif element_type == "load":
            indices = [net.load[net.load.name.str.endswith(str(name))].index[0] for name in names]
        elif element_type == "line":
            indices = [net.line[net.line.name.str.endswith(str(name))].index[0] for name in names]
    except IndexError:
        indices = []
    return indices


def get_names_from_indices(net, indices, element_type="bus"):
    names = []
    if element_type == "bus":
        names = list(str(net.bus.loc[indices].name))
    elif element_type == "load":
        names = list(str(net.load.loc[indices].name))
    elif element_type == "line":
        names = list(str(net.line.loc[indices].name))
    return names


def init_random():
    r_seed = configuration.config.getint("DEFAULT", "seed", fallback=SystemRandom())
    seed(r_seed)
    getLogger("main").info(f"Random seed: '{r_seed}'")


def get_number_of_slots_per_week():
    return configuration.config.getint("time", "number_of_time_slots", fallback=96) * \
        configuration.config.getint("time", "number_of_days", fallback=7)


def get_current_time_string(i):
    number_of_timeslots_per_day = configuration.config.getint("time", "number_of_time_slots", fallback=96)
    number_of_days_per_week = configuration.config.getint("time", "number_of_days", fallback=7)
    number_of_slots_per_week = number_of_timeslots_per_day * number_of_days_per_week
    return str(int(i / (number_of_slots_per_week / number_of_days_per_week / 24)) - int(i / number_of_timeslots_per_day)
               * 24) + ":" + '%02d' % int((i % (number_of_timeslots_per_day / 24))
                                          * (24 / number_of_timeslots_per_day * 60))


def create_bus_bus_map(net1, net2):
    bus_map = dict()
    missing = list(net1.bus.index)
    for _, load in net1.load.iterrows():
        if any(net2.load.name == load['name']):
            bus1 = load['bus']
            bus_map[bus1] = net2.bus.name[net2.load.bus[net2.load.name == load['name']]].index[0]
            if bus1 in missing:
                missing.remove(bus1)

    if len(missing) == 0:
        return bus_map

    graph1 = ppt.create_nxgraph(net1, respect_switches=True, include_impedances=False, calc_branch_impedances=False)
    graph2 = ppt.create_nxgraph(net2, respect_switches=True, include_impedances=False, calc_branch_impedances=False)

    # Pop trafo, not interesting
    trafo_node = 0 if net1.trafo.empty else int(net1.trafo.lv_bus[0])
    if trafo_node in missing:
        missing.remove(trafo_node)
    if not net1.trafo.empty:
        missing.remove(int(net1.trafo.hv_bus[0]))

    for rem_bus in missing:
        neigh1 = list(graph1.neighbors(rem_bus))

        if len(neigh1) == 1:
            if neigh1[0] in bus_map:
                bus_map[rem_bus] = bus_map[neigh1[0]]
                continue
            else:
                neighs = list(graph1.neighbors(neigh1[0]))
                while all(neigh not in bus_map for neigh in neighs):
                    neighst = []
                    neighs = [neighst + list(graph1.neighbors(n)) for n in neighs]
                    neighs = [i for i in chain.from_iterable(neighs)]
                bus_map[rem_bus] = bus_map[[neigh for neigh in neighs if neigh in bus_map][0]]
                continue

        neigh2 = set()
        closest_neighbour = -1
        for n1 in neigh1:
            if n1 in bus_map:
                n2 = bus_map[n1]
                closest_neighbour = n2
                if len(neigh2) == 0:
                    neigh2 = set(graph2.neighbors(n2))
                else:
                    neigh2 = neigh2.intersection(set(graph2.neighbors(n2)))
        if len(neigh2) == 0:
            if closest_neighbour != -1:
                bus_map[rem_bus] = closest_neighbour
            else:
                while all(neigh not in bus_map for neigh in neigh1):
                    neighst = []
                    neigh1 = [neighst + list(graph1.neighbors(n)) for n in neigh1]
                    neigh1 = [i for i in chain.from_iterable(neigh1)]
                bus_map[rem_bus] = bus_map[[neigh for neigh in neigh1 if neigh in bus_map][0]]
        else:
            bus_map[rem_bus] = neigh2.pop()

    return bus_map
