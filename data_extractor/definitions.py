from enum import Enum, auto

from data_extractor.operation import Operation


class GeneratorType(Enum):
    ESTIMATION = "state_estimation"
    LOADFLOW = "loadflow"
    DIFFERENCE = "difference"
    FILE = "file"


class DataKind(Enum):
    NODE_VOLTAGE = "node_voltage_pu"
    NODE_VOLTAGE_ANGLE = "node_voltage_angle_deg"
    NODE_ACTIVE_POWER = "node_p_w"
    NODE_REACTIVE_POWER = "node_q_var"
    LINE_CURRENT = "line_current_a"
    LINE_TO_ACTIVE_POWER = "line_to_p_kw"
    LINE_TO_REACTIVE_POWER = "line_to_q_kvar"
    LINE_FROM_ACTIVE_POWER = "line_from_p_kw"
    LINE_FROM_REACTIVE_POWER = "line_from_q_kvar"
    LINE_LOADING = "line_loading_percent"
    LINE_ACTIVE_POWER_LOSS = "line_p_loss_w"
    LINE_REACTIVE_POWER_LOSS = "line_q_loss_var"
    TRAFO_ACTIVE_POWER_LOSS = "trafo_p_loss_w"
    TRAFO_REACTIVE_POWER_LOSS = "trafo_q_loss_var"
    TRAFO_ACTIVE_POWER_MV = "trafo_p_mv_side_kw"
    TRAFO_REACTIVE_POWER_MV = "trafo_q_mv_side_kvar"
    TRAFO_ACTIVE_POWER_LV = "trafo_p_lv_side_kw"
    TRAFO_REACTIVE_POWER_LV = "trafo_q_lv_side_kvar"
    TRAFO_CURRENT_MV = "trafo_current_mv_side_a"
    TRAFO_CURRENT_LV = "trafo_current_lv_side_a"
    TRAFO_LOADING = "trafo_loading_percent"
    TRAFO_VOLTAGE_MV = "trafo_voltage_mv_side_pu"
    TRAFO_VOLTAGE_LV = "trafo_voltage_lv_side_pu"
    TRAFO_VOLTAGE_ANGLE_MV = "trafo_voltage_angle_mv_side_deg"
    TRAFO_VOLTAGE_ANGLE_LV = "trafo_voltage_angle_lv_side_deg"
    MEASUREMENTS = "measurements"


data_kind_to_element = \
    dict(node_voltage_pu="vm_pu",
         node_voltage_angle_deg="va_degree",
         node_p_w="p_mw",
         node_q_var="q_mvar",
         line_current_a="i_ka",
         line_to_p_kw="p_to_mw",
         line_to_q_kvar="q_to_mvar",
         line_from_p_kw="p_from_mw",
         line_from_q_kvar="q_from_mvar",
         line_loading_percent="loading_percent",
         line_p_loss_w="pl_mw",
         line_q_loss_var="ql_mvar",
         trafo_p_loss_w="pl_mw",
         trafo_q_loss_var="ql_mvar",
         trafo_p_mv_side_kw="p_hv_mw",
         trafo_q_mv_side_kvar="q_hv_mvar",
         trafo_p_lv_side_kw="p_lv_mw",
         trafo_q_lv_side_kvar="q_lv_mvar",
         trafo_current_mv_side_a="i_hv_ka",
         trafo_current_lv_side_a="i_lv_ka",
         trafo_loading_percent="loading_percent",
         trafo_voltage_mv_side_pu="vm_hv_pu",
         trafo_voltage_lv_side_pu="vm_lv_pu",
         trafo_voltage_angle_lv_side_deg="va_hv_degree",
         trafo_voltage_angle_mv_side_deg="va_lv_degree",
         measurements="")

data_kind_to_element_3ph = data_kind_to_element.copy()
data_kind_to_element_3ph["line_p_loss_w"] = "p_l_mw"
data_kind_to_element_3ph["line_q_loss_var"] = "q_l_mvar"
data_kind_to_element_3ph["trafo_q_loss_var"] = "q_l_mvar"
data_kind_to_element_3ph["trafo_p_loss_w"] = "p_l_mw"

data_kind_to_conversion_multiplier = \
    {
        "node_voltage_pu": 1,
        "node_voltage_angle_deg": 1,
        "node_p_w": 1e6,
        "node_q_var": 1e6,
        "line_current_a": 1e3,
        "line_to_p_kw": 1e3,
        "line_to_q_kvar": 1e3,
        "line_from_p_kw": 1e3,
        "line_from_q_kvar": 1e3,
        "line_loading_percent": 1,
        "line_p_loss_w": 1e6,
        "line_q_loss_var": 1e6,
        "trafo_p_loss_w": 1e6,
        "trafo_q_loss_var": 1e6,
        "trafo_p_mv_side_kw": 1e3,
        "trafo_q_mv_side_kvar": 1e3,
        "trafo_p_lv_side_kw": 1e3,
        "trafo_q_lv_side_kvar": 1e3,
        "trafo_current_mv_side_a": 1e3,
        "trafo_current_lv_side_a": 1e3,
        "trafo_loading_percent": 1,
        "trafo_voltage_mv_side_pu": 1,
        "trafo_voltage_lv_side_pu": 1,
        "trafo_voltage_angle_lv_side_deg": 1,
        "trafo_voltage_angle_mv_side_deg": 1,
        "measurements": 1
    }

default_format = "%.2f"
data_kind_to_format = \
    {
        "node_voltage_pu": "%.6f",
        "node_voltage_angle_deg": "%.4f",
        "node_p_w": default_format,
        "node_q_var": default_format,
        "line_current_a": "%.4f",
        "line_to_p_kw": default_format,
        "line_to_q_kvar": default_format,
        "line_from_p_kw": default_format,
        "line_from_q_kvar": default_format,
        "line_loading_percent": default_format,
        "line_p_loss_w": "%.4f",
        "line_q_loss_var": default_format,
        "trafo_p_loss_w": default_format,
        "trafo_q_loss_var": default_format,
        "trafo_p_mv_side_kw": default_format,
        "trafo_q_mv_side_kvar": default_format,
        "trafo_p_lv_side_kw": default_format,
        "trafo_q_lv_side_kvar": default_format,
        "trafo_current_mv_side_a": default_format,
        "trafo_current_lv_side_a": default_format,
        "trafo_loading_percent": default_format,
        "trafo_voltage_mv_side_pu": "%.6f",
        "trafo_voltage_lv_side_pu": "%.6f",
        "trafo_voltage_angle_lv_side_deg": "%.4f",
        "trafo_voltage_angle_mv_side_deg": "%.4f",
        "measurements": "%.4f"
    }


class OutputMode(Enum):
    CSV = auto(),
    EXCEL = auto()


operation_to_name = {
    Operation.MEAN: "Mean",
    Operation.ABS_MEAN: "Absolute mean",
    Operation.VARIANCE: "Variance",
    Operation.ABS_VARIANCE: "Absolute variance",
    Operation.RMS: "Root mean square"
}


def data_kind_to_quantity(data_kind):
    if "voltage" in data_kind:
        return "V"
    elif "_p_" in data_kind:
        return "P"
    elif "_q_" in data_kind:
        return "Q"
    elif "current" in data_kind:
        return "I"
    else:
        raise ValueError(f"Unknown data type quantity {data_kind}")
