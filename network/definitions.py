from enum import Enum


class NetworkKind(Enum):
    CLOSEST = "closest"
    EXACT = "exact"
    CUT_TO_PIECES = "cut_to_pieces"


class Network(Enum):
    BESNICA = "besnica"
    BESNICA_REDUCED = "besnica_reduced"
    PILOT = "pilot"
    CONTROLLED = "controlled"
    MEDIUM_VOLTAGE = "medium_voltage"


class NetworkId(Enum):
    ID_18680 = 18680
    ID_44333 = 44333
    ID_44600 = 44600
    ID_20667 = 20667
    ID_23427 = 23427
    ID_99999 = 99999
    ID_220018 = 220018


network_name = {
    NetworkId.ID_18680: "Baracs",
    NetworkId.ID_20667: "Gyor",
    NetworkId.ID_44600: "Balatonszepezd",
    NetworkId.ID_44333: "Balatonakali",
    NetworkId.ID_23427: "Janossomorja",
    NetworkId.ID_99999: "Nagyvenyim",
    NetworkId.ID_220018: "Movar"
}


HIGH_VOLTAGE_TRAFO_NAME = "HV/MV"
