from enum import Enum


class BasicScenario(Enum):
    SC_1 = "1"
    SC_1m = "1m"
    SC_2 = "2"
    SC_2m = "2m"
    SC_2mm = "2mm"
    REFERENCE = "reference"
    PV = "pv"
    BASIC = "basic"


class ControlledScenario(Enum):
    SC_1_NON_CONTROLLED = "not_controlled"
    SC_2_CONTROLLED = "controlled"
    SC_3_CONTROLLED_WITH_PSEUDO_MEASUREMENTS = "controlled_with_pseudo"


class PvScenario(Enum):
    SC_1_BASIC = "basic_pv"
    SC_2_CONTROLLED = "controlled_pv"
    SC_3_PV = "pv_scen"
    SC_4_MOD_PV = "mod_pv"


class Scenario1Subscenario(Enum):
    NO_SM = 'A'
    SM = 'B'


class Scenario2Subscenario(Enum):
    SC_2m = 'A'
    SC_2mm = 'B'


class Scenario3Subscenario(Enum):
    Profile = 'A'
    TMY = 'B'
    CS = 'C'


subscenario = {
    PvScenario.SC_1_BASIC: Scenario1Subscenario,
    PvScenario.SC_2_CONTROLLED: Scenario2Subscenario,
    PvScenario.SC_3_PV: Scenario3Subscenario,
    PvScenario.SC_4_MOD_PV: Scenario3Subscenario
}


class SmartMeterScenario(Enum):
    SC_1_NoMeas = "1_No_meas"
    SC_2_Current = "2_Current"
    SC_3_Voltage = "3_Voltage"
    SC_4_Voltage_and_current = "4_Current_and_voltage"
    SC_5_Dozsa_1 = "5_Dozsa_1"
    SC_6_Dozsa_2 = "6_Dozsa_2"


scenario_to_deviation = {
    BasicScenario.SC_1: 2540.47 / 1e6,
    BasicScenario.SC_1m: 2539.25 / 1e6,
    BasicScenario.SC_2: 884.116 / 1e6,
    BasicScenario.SC_2m: 940.834 / 1e6,
    BasicScenario.SC_2mm: 275.357 / 1e6
}


scenario_to_deviation_controlled = {
    BasicScenario.SC_1: 123225 / 1e6,
    BasicScenario.SC_1m: 123146 / 1e6,
    BasicScenario.SC_2: 119048 / 1e6,
    BasicScenario.SC_2m: 119195 / 1e6,
    BasicScenario.SC_2mm: 127572 / 1e6
}
