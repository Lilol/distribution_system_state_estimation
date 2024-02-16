from enum import Enum


class NetworkId(Enum):
    ID_18680 = "A"
    ID_20667 = "B"
    ID_44333 = "C"
    ID_44600 = "D"

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value


network_name = {NetworkId.ID_18680: "Baracs", NetworkId.ID_20667: "Gyor", NetworkId.ID_44600: "Balatonszepezd",
                NetworkId.ID_44333: "Balatonakali"}


class Season(Enum):
    Spring = "Spring"
    Summer = "Summer"
    Autumn = "Autumn"
    Winter = "Winter"


# weeks_of_season = {Season.Winter: [0, 1, 2, 3, 23, 24], Season.Spring: [4, 5, 6, 7, 8, 9],
#                    Season.Summer: [10, 11, 12, 13, 14, 15, 16], Season.Autumn: [17, 18, 19, 20, 21, 22]}

weeks_of_season = {Season.Winter: [3], Season.Spring: [4, 5, 6, 7, 8, 9],
                   Season.Summer: [10, 11, 12, 13, 14, 15, 16], Season.Autumn: [17]}

class Scenario(Enum):
    SC_1 = "SC_1_BASIC"
    SC_2 = "SC_2_CONTROLLED"
    SC_3 = "SC_3_PV"


scenario_name = {Scenario.SC_1: "Basic scenario", Scenario.SC_2: "Controlled consumers", Scenario.SC_3: "PV production"}


class Scenario1(Enum):
    NO_SM = "NO_SM"
    SM = "SM"


class Scenario2(Enum):
    SC_2m = "SC_2m"
    SC_2mm = "SC_2mm"


class Scenario3(Enum):
    CS = "CS"
    Profile = "Profile"
    TMY = "TMY"


scen_to_subscen = {Scenario.SC_1: Scenario1, Scenario.SC_2: Scenario2, Scenario.SC_3: Scenario3}


class Param(Enum):
    VOLTAGE = "node_voltage_pu"
    PHASE = "node_voltage_angle_deg"


def week_to_index(week):
    return [i * (w + 1) for w in week for i in range(1, 97)]


def season_to_index(season):
    list_of_lists = [weeks_of_season[s] for s in season]
    return week_to_index([item for sublist in list_of_lists for item in sublist])


def select_time(df, pack=None, season=None, week=None):
    if season is not None:
        return df.loc[season_to_index(pack_val(season))]
    elif week is not None:
        return df.loc[season_to_index(pack_val(week))]
    elif hasattr(pack, "season"):
        return df.loc[season_to_index(pack.season)]
    elif hasattr(pack, "week"):
        return df.loc[week_to_index(pack.week)]
    else:
        return df


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def pack_val(val):
    return val if is_iterable(val) else [val]


class DifferentiateBy(Enum):
    NONE = None
    NODE = "rows"
    TIME = "columns"


class Calculation(Enum):
    RMS = "Root mean square error"
    MAE = "Mean average error"
    MRE = "Mean relative error"
    VAR = "VAR"


def get_param_name(param, error):
    name = f""

    if param == Param.VOLTAGE:
        name = fr"$\Delta u_{{"
    elif param == Param.PHASE:
        name = fr"$\Delta \theta_{{"

    if error == Calculation.RMS:
        name = fr"{name}\mathrm{{RMS}}}}"
    elif error == Calculation.MAE:
        name = fr"{name}\mathrm{{MAE}}}}"
    elif error == Calculation.MRE:
        name = fr"{name}\mathrm{{MRE}}}}"
    elif error == Calculation.MRE:
        name = fr"{name}\mathrm{{VAR}}}}"
    else:
        raise ValueError(f"Unknown error type {error}")

    if param == Param.VOLTAGE and error != Calculation.MRE:
        name = fr"{name}$\ [p.u.]"
    elif param == Param.PHASE and error != Calculation.MRE:
        name = fr"{name}\ [^\circ]$"
    elif error == Calculation.MRE:
        name = fr"{name}\ [-]$"
    return name
