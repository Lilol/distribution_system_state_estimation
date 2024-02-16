import utility.configuration as configuration
from data_extractor.definitions import DataKind
from measurement.definitions import SmartMeterScenario

endpoint_nodes = {
    "MET1": 0,
    "MET2": 12,
    "MET3": 26,
    "MET4": 62,
    "MET5": 94,
    "MET6": 91
}

trafo_nodes = {
    "TR1": 113,
    "TR2": 43,
    "TR3": 7,
    "TR4": 9,
    "TR5": 102,
}

trafo_line_names = {
    "TR1": "9756_0",
    "TR2": "1471_0",
    "TR3": "8820_0",
    "TR4": "1002_1",
    "TR5": "1232_1",
}

trafo_lines = {
    "TR1": 108,
    "TR2": 59,
    "TR3": 20,
    "TR4": 7,
    "TR5": 95,
}

symbol_name_to_long_name = {
    "TR1": "Táppont 1",
    "TR2": "Táppont 2",
    "TR3": "Táppont 3",
    "TR4": "Táppont 4",
    "TR5": "Táppont 5",
    "MET1": "Végpont 1",
    "MET2": "Végpont 2",
    "MET3": "Végpont 3",
    "MET4": "Végpont 4",
    "MET5": "Végpont 5",
    "MET6": "Végpont 6"
}


def to_sm_name(name, data_kind):
    if data_kind == DataKind.NODE_VOLTAGE:
        for k, v in trafo_nodes.items():
            if v != name:
                continue
            return symbol_name_to_long_name[v]
        for k, v in endpoint_nodes.items():
            if v != name:
                continue
            return symbol_name_to_long_name[v]
    elif data_kind == DataKind.LINE_CURRENT:
        for k, v in endpoint_nodes.items():
            if v not in name:
                continue
            return symbol_name_to_long_name[v]


def get_measurement_types_based_on_scenario():
    sc = configuration.config.get("scenario", "scenario")
    if sc == SmartMeterScenario.SC_1_NoMeas:
        return []
    elif sc == SmartMeterScenario.SC_2_Current:
        return "I",
    elif sc == SmartMeterScenario.SC_3_Voltage:
        return "V",
    elif sc in (SmartMeterScenario.SC_4_Voltage_and_current, SmartMeterScenario.SC_5_Dozsa_1, SmartMeterScenario.SC_6_Dozsa_2):
        return "V", "I"
    else:
        raise ValueError(f"Unknown scenario {sc}")


def get_meas_points_based_on_scenario():
    sc = configuration.config.get("scenario", "scenario")
    if sc == SmartMeterScenario.SC_5_Dozsa_1:
        return "TR1", "TR2", "TR3", "TR4", "TR5", "MET1", "MET2", "MET5", "MET4"
    elif sc == SmartMeterScenario.SC_6_Dozsa_2:
        return "TR1", "TR2", "TR3", "TR4", "TR5", "MET1", "MET2", "MET5", "MET3"
    else:
        return None


def element_selector(element, meas_type):
    if "TR" in element:
        if meas_type == "V":
            return trafo_nodes[element], "bus"
        else:
            assert meas_type == "I", "Transformer quantity must either be voltage or current."
            return trafo_lines[element], "line"
    else:
        assert "MET" in element, "Non-transformer quantities must be 'SM'-measured."
        return endpoint_nodes[element], "bus"
