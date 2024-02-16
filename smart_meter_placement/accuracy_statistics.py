from logging import getLogger

import utility.configuration as configuration
from data_extractor.derived_data import Operation
from smart_meter_placement.checkpoint_restart import get_accuracies_and_fixed_meters, get_fixed_meters
from smart_meter_placement.get_circuits import get_ordered_circuits, get_pv_circuit


class AccuracyStatistics:
    def __init__(self):
        # List of buses fixed sofar
        self.__fixed_meters = dict()
        self.__accuracies = dict()
        self.__circuits = list()
        self.__first_non_empty_circuit = -1
        self.__pv_circuit = -1
        self.__logger = getLogger("smart_meter_placement.globals.AccuracyStatistics")
        self.__meter_fixed = False

    def initialized(self):
        return len(self.__circuits) != 0

    def reinitialize(self, net):
        self.__meter_fixed = False
        self.__logger.info("Reinitializing meter placement...")
        self.__fixed_meters = dict()
        self.__accuracies = dict()
        self.__circuits = get_ordered_circuits(net)
        assert not (configuration.config.getboolean("scenario", "metering_scenario_checkpoint_restart") and
                    configuration.config.getboolean("scenario",
                                                    "metering_position_use_pv")), "Checkpoint restart and PV positioning " \
                                                                                  "cannot be true at the same time."
        if configuration.config.getboolean("scenario", "metering_scenario_checkpoint_restart"):
            self.__first_non_empty_circuit = self.__clear_empty_circuits()
            self.__fixed_meters, self.__accuracies = get_accuracies_and_fixed_meters(self.__first_non_empty_circuit)
        if configuration.config.getboolean("scenario", "metering_position_use_pv"):
            self.__pv_circuit = get_pv_circuit(self.__circuits)
            self.__fixed_meters = dict.fromkeys(get_fixed_meters(circuit_idx=0, from_config=True))

    def __clear_empty_circuits(self):
        for i, c in enumerate(list(self.__circuits)):
            if not c.is_empty():
                return i
            else:
                self.__circuits.remove(c)
        return -1

    def reinitialize_accuracy(self):
        self.__logger.info("Reinitializing meter precision vector...")
        self.__accuracies = dict()

    def fix_most_accurate_meter(self):
        self.__meter_fixed = True
        if len(self.__accuracies) > 0:
            self.__logger.info("Fixing most accurate meter...")
            meter = min(self.__accuracies, key=self.__accuracies.get)
            self.__fixed_meters[meter] = self.__accuracies[meter]
        else:
            self.__logger.error("No precisions saved.")

    def get_meters_fixed_sofar(self):
        return list(self.__fixed_meters.keys())

    def get_fixed_meter_precisions(self):
        return list(self.__fixed_meters.values())

    def get_accuracy(self, metering_bus):
        return self.__accuracies[metering_bus]

    def get_ordered_circuits(self):
        return self.__circuits

    def n_circuits(self):
        return len(self.__circuits) + self.__first_non_empty_circuit

    def get_first_non_empty_circuit_num(self):
        return self.__first_non_empty_circuit

    def n_finished_buses(self):
        return len(self.__accuracies)

    def get_circuit_roots(self):
        for c in self.__circuits:
            yield c.root, c.line

    def circuit_root_nodes(self):
        return [c.root for c in self.__circuits]

    def add_accuracy(self):
        p = data_extractor.retrieve_derived_data("node_voltage_pu", Operation.RMS).iloc[-1]
        meter = configuration.config.getint("scenario", "meter_positioning_bus")
        self.__accuracies[meter] = abs(p)
        self.__logger.info("Smart meter precision saved for meter '" + str(meter) + "', precision: '" + str(abs(p)) +
                           "'")

    def get_pv_circuit(self):
        return self.__circuits[self.__pv_circuit]

    def get_pv_circuit_index(self):
        return self.__pv_circuit

    def any_meter_fixed(self):
        return self.__meter_fixed


accuracy_statistics = AccuracyStatistics()
data_extractor = None
