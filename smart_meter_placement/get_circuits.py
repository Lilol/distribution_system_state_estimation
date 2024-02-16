import networkx as nx
import pandapower.topology as ppt

import utility.configuration as configuration
from network.definitions import NetworkId
from utility.collect_load_consumptions import collect_load_consumptions


class Circuit:
    def __init__(self, root_node, root_line, circuit_nodes, save_root_as_part_of_circuit=False):
        self.nodes = circuit_nodes
        if save_root_as_part_of_circuit:
            self.nodes = [root_node] + self.nodes
        self.root = root_node
        self.line = root_line
        self.sum_yc = 0
        self.sum_pv_kwp = 0
        self.__idx = 0

    def clear(self, clear_until=None):
        if clear_until is None:
            self.nodes = []
        else:
            temp = self.nodes.index(clear_until)
            self.nodes = self.nodes[temp:]

    def is_member(self, node):
        return node in self.nodes or node == self.root

    def add_yearly_consumption(self, yearly_consumptions, add_pv_data=False):
        yc = list(yearly_consumptions)
        self.sum_yc += sum(yc[0:1])
        if add_pv_data:
            self.sum_pv_kwp += yc[2]

    def is_empty(self):
        return len(self.nodes) == 0

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        if self.__idx < len(self.nodes):
            return self.nodes[self.__idx]
        else:
            raise StopIteration

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)


def remove_unconnected_components(graph, root_node):
    connected_components = nx.connected_components(graph)
    for c in connected_components:
        if root_node in graph.subgraph(c).nodes:
            graph.remove_nodes(graph.subgraph(c).nodes)


def build_dummy_circuits():
    circuits = [Circuit(3, 2, [1])]
    return circuits


def get_circuits(net, respect_switches=True, include_unconnected_components=False):
    graph = ppt.create_nxgraph(net, respect_switches=respect_switches, include_impedances=False,
                               calc_branch_impedances=False)
    is_connected = nx.is_connected(graph)
    root_node = 0 if net.trafo.empty else int(net.trafo.lv_bus[0])
    if not net.trafo.empty:
        # Split HV node from graph to not store HV-part as a circuit
        graph.remove_node(int(net.trafo.hv_bus[0]))

    # if graph is not connected, remove components that are not connected to the "root node" = trafo
    # if not include_unconnected_components and not is_connected:
    #     remove_unconnected_components(graph, root_node)

    # Workaround for multi-edge circuit-start lines: filter start nodes that have multiple incoming edges
    unique = []
    circuit_start = []
    for edge in graph.edges(root_node, keys=True):
        if edge[1] not in unique:
            unique.append(edge[1])
            circuit_start.append((edge[1], edge[2][1]))
    graph.remove_node(root_node)

    save_root_as_part_of_circuit = configuration.config.get("input", "network_id") == NetworkId.ID_20667
    circuits = [Circuit(root, line, [v for _, v, _ in nx.algorithms.edge_bfs(graph, root)],
                        save_root_as_part_of_circuit)
                for root, line in circuit_start]

    return circuits


def get_ordered_circuits(net, respect_switches=True, no_checkpoint_restart=False):
    if configuration.config.getboolean("testing", "on", False):
        return build_dummy_circuits()

    circuits = get_circuits(net, respect_switches, False)
    load_consumptions = collect_load_consumptions(na_values=0)
    use_pv_data = configuration.config.getboolean("scenario", "metering_position_use_pv")

    for fid, cons in load_consumptions.iterrows():
        try:
            bus = int(net.load[net.load.name == fid].bus)
        except TypeError:
            print(f"Load '{str(fid)}' is missing from the network.")
            continue
        c = [c for c in circuits if c.is_member(bus)]
        if len(c) == 1:
            c[0].add_yearly_consumption(cons, use_pv_data)
        else:
            for circ in c:
                circ.add_yearly_consumption(cons)
            print(f"Node '{str(bus)}' is not part of any circuit or part of multiple circuits.")

    circuits = sorted(circuits, key=lambda x: x.sum_yc, reverse=True)

    if configuration.config.getboolean("scenario",
                                       "metering_scenario_checkpoint_restart") and not no_checkpoint_restart:
        if configuration.config.has_option("scenario", "restart_from_bus"):
            start_from = configuration.config.getint("scenario", "restart_from_bus")
            for c in circuits:
                if c.is_member(start_from):
                    c.clear(start_from)
                    break
                c.clear()
        else:
            print("Bus to restart from must be specified when checkpoint restart is active!")

    return circuits


def get_pv_circuit(circuits):
    return circuits.index(max(circuits, key=lambda x: x.sum_pv_kwp))
