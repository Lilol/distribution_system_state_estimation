from enum import Enum

import utility.configuration as configuration
from network.definitions import NetworkId
from smart_meter_placement.accuracy_statistics import accuracy_statistics
from utility.utils import get_number_of_slots_per_week


class FictiveMeasurementError(Enum):
    FIXED_BUS_U_PU = 0.005  # std_dev
    METERED_BUS_U_PU = 0.005  # std_dev
    FEEDER_U_PU = 0.005  # std_dev
    FEEDER_I_kA = 0.3 / 1000  # std_dev
    FEEDER_P_MW = 0.00001
    FEEDER_Q_MVar = 0.00001


def create_meter_placement_measurements(measurements, measurement_store, net):
    val_source = configuration.config.get("validation", "validation_source")
    if val_source == "file":
        create_meter_placement_measurements_from_file(measurements, measurement_store, net)
    elif val_source == "algorithm":
        create_meter_placement_measurements_from_algorithm(measurements, measurement_store)
    else:
        raise ValueError(f"Unknown validation source: {val_source}")


def create_meter_placement_measurements_from_file(measurements, measurement_store, net):
    week_length = get_number_of_slots_per_week()
    table_u, table_i = measurement_store.get_measurement_tables()
    # U, I measurements at feeder
    for bus_idx, line_idx in accuracy_statistics.get_circuit_roots():
        measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                     element_idx=int(bus_idx), data=table_u[net.bus.name[bus_idx]], count=week_length,
                                     std_dev=FictiveMeasurementError.FEEDER_U_PU.value)
        measurements.add_measurement(name=f"I_{str(line_idx)}", measurement_type="i", element_type="line",
                                     element_idx=int(line_idx), data=table_i[net.line.name[line_idx]] / 1000,
                                     count=week_length, std_dev=FictiveMeasurementError.FEEDER_I_kA.value, side="to")

    # U measurements at fixed meters
    for bus_idx in accuracy_statistics.get_meters_fixed_sofar():
        if bus_idx == configuration.config.getint("scenario", "meter_positioning_bus"):
            continue
        measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                     element_idx=bus_idx, data=table_u[net.bus.name[bus_idx]], count=week_length,
                                     std_dev=FictiveMeasurementError.FIXED_BUS_U_PU.value)

    # U measurement at currently positioned bus
    bus_idx = configuration.config.getint("scenario", "meter_positioning_bus")
    measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                 element_idx=bus_idx, data=table_u[net.bus.name[bus_idx]], count=week_length,
                                 std_dev=FictiveMeasurementError.METERED_BUS_U_PU.value)


def create_meter_placement_measurements_from_algorithm(measurements, measurement_store):
    validation_net = measurement_store.get_validation_network()
    if not configuration.config.get("input", "network_id") == NetworkId.ID_20667:
        for bus_idx, line_idx in accuracy_statistics.get_circuit_roots():
            measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                         element_idx=int(bus_idx), std_dev=FictiveMeasurementError.FEEDER_U_PU.value,
                                         net=validation_net)
            measurements.add_measurement(name=f"P_{str(bus_idx)}", measurement_type="p", element_type="bus",
                                         element_idx=int(bus_idx), std_dev=FictiveMeasurementError.FEEDER_P_MW.value,
                                         net=validation_net)
            measurements.add_measurement(name=f"Q_{str(bus_idx)}", measurement_type="q", element_type="bus",
                                         element_idx=int(bus_idx), std_dev=FictiveMeasurementError.FEEDER_Q_MVar.value,
                                         net=validation_net)
            if not configuration.config.getboolean("scenario", "metering_position_skip_i_measurements"):
                measurements.add_measurement(name=f"I_{str(line_idx)}", measurement_type="i", element_type="line",
                                             element_idx=int(line_idx),
                                             std_dev=FictiveMeasurementError.FEEDER_I_kA.value, side="to",
                                             net=validation_net)
    else:
        bus_index = validation_net.trafo.lv_bus.at[0]
        measurements.add_measurement(name="V_trafo", measurement_type="v", element_type="bus", element_idx=bus_index,
                                     data=1, std_dev=FictiveMeasurementError.FEEDER_U_PU.value, net=validation_net)

    # U measurements at fixed meters
    for bus_idx in accuracy_statistics.get_meters_fixed_sofar():
        measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                     element_idx=bus_idx, std_dev=FictiveMeasurementError.FIXED_BUS_U_PU.value,
                                     net=validation_net)

    # U measurement at currently positioned bus
    bus_idx = configuration.config.getint("scenario", "meter_positioning_bus")
    measurements.add_measurement(name=f"V_{str(bus_idx)}", measurement_type="v", element_type="bus",
                                 element_idx=bus_idx, std_dev=FictiveMeasurementError.METERED_BUS_U_PU.value,
                                 net=validation_net)
