from collections import OrderedDict
from enum import Enum
from logging import getLogger

from pandas import read_excel

import measurement.definitions
import utility.configuration as configuration
from measurement.definitions import PvScenario, Scenario1Subscenario, subscenario
from network.definitions import NetworkId
from network.network_factory import network_factory
from smart_meter_placement.accuracy_statistics import accuracy_statistics


class Action(Enum):
    REINITIALIZE_NETWORK = 0
    REINITIALIZE_OUTPUT_WRITER = 1
    FINISH_OUTPUT_WRITING = 2
    SAVE_METER_ACCURACY = 3
    FIX_MOST_ACCURATE_METER = 4
    REINIT_METER_PLACEMENT = 5
    REINIT_PRECISION = 6


def scenario_maker(scenarios: dict):
    if "position_meter" in scenarios["scenarios"]:
        return MeterPositioningScenario(scenarios)
    elif type(scenarios["scenarios"][0]) == PvScenario:
        return HmkeScenario(scenarios)

    try:
        measurement.definitions.ControlledScenario(scenarios["scenarios"][0])
        return ControlledScenario(scenarios)
    except:
        return Scenario(scenarios)


def convert_sheet_to_scenario(scenario, dataframe):
    scenarios = []
    no_of_weeks = configuration.config.getint("time", "number_of_weeks")
    scenario_prototype = OrderedDict({"weeks": list(range(1, no_of_weeks + 1)),
                                      "networks": [nw.value for nw in NetworkId if nw not in
                                                   (NetworkId.ID_99999, NetworkId.ID_23427)],
                                      "subscenarios": [sc.value for sc in subscenario[scenario]],
                                      "scenarios": [scenario]})
    # scenario_prototype["weeks"] = [21, 14, 7, 1, 2, 3]
    if dataframe.all(axis=None) and scenario != PvScenario.SC_1_BASIC:
        return [scenario_maker(scenario_prototype)]

    for col in dataframe.columns:
        if ~dataframe[col].any():
            continue

        sc = scenario_prototype.copy()
        sc["subscenarios"] = [subscenario[scenario](col).value]

        if scenario == PvScenario.SC_1_BASIC and subscenario[scenario](col) == Scenario1Subscenario.NO_SM:
            sc["weeks"] = list(range(1, (52 if no_of_weeks == 26 else no_of_weeks) + 1))
            # sc["weeks"] = [1, 14, 31, 51]

        if dataframe[col].all():
            scenarios.append(scenario_maker(sc))
        else:
            for nw, el in dataframe[col].iteritems():
                if not el:
                    continue
                sc["networks"] = [str(NetworkId(nw).value)]
                scenarios.append(scenario_maker(sc))
    return scenarios


def convert_excel_to_scenarios():
    sheet_name_to_scenario = {'SC1': PvScenario.SC_1_BASIC, 'SC2': PvScenario.SC_2_CONTROLLED,
                              'SC3': PvScenario.SC_3_PV}
    scenarios = []
    df = read_excel(configuration.config.get("multiple_run", "scenario_excel"), None, index_col=0, engine='openpyxl')
    for sheet_name, scen_table in df.items():
        scenarios = scenarios + convert_sheet_to_scenario(sheet_name_to_scenario[sheet_name], scen_table)
    # init scenario with all options being true
    return scenarios


def scenario_factory():
    if configuration.config.getboolean("multiple_run", "pv_scenario"):
        scenarios = convert_excel_to_scenarios()
    else:
        scenarios = [scenario_maker(s) for _, s in configuration.config.get("multiple_run", "scenarios").items()]
    return scenarios


class Setting:
    def __init__(self, setting_list, beginning_actions=None, end_actions=None):
        self._list = setting_list
        self._idx = 0
        self._end_actions = end_actions
        self._beginning_actions = beginning_actions

    def init(self):
        self._idx = 0

    def set_settings(self, settings):
        self._list = settings

    def add_actions(self, beginning_actions=None, end_actions=None):
        if beginning_actions:
            if self._beginning_actions:
                self._beginning_actions.extend(beginning_actions)
            else:
                self._beginning_actions = beginning_actions
        if end_actions:
            if self._end_actions:
                self._end_actions.extend(end_actions)
            else:
                self._end_actions = end_actions

    def get_actions(self):
        actions = []
        if self._idx == len(self._list) - 1 and self._end_actions:
            actions.extend(self._end_actions)
        if self._idx == 0 and self._beginning_actions:
            actions.extend(self._beginning_actions)
        return actions

    def get_setting(self):
        return self._list[self._idx]

    def increment(self):
        self._idx += 1
        if self._idx == len(self._list):
            self._idx = 0
            return False
        return True

    def is_new_start(self):
        return self._idx == 0

    def is_final(self):
        return self._idx == len(self._list) - 1


class Setting2D(Setting):
    def __init__(self, setting_list, beginning_actions=None, end_actions=None, between_rows_actions=None):
        super(Setting2D, self).__init__(setting_list, beginning_actions=beginning_actions, end_actions=end_actions)
        self.__between_rows_actions = between_rows_actions
        self.__row_idx = 0

    def init(self):
        super(Setting2D, self).init()
        self.__row_idx = 0

    def set_settings(self, settings):
        self._list = settings

    def add_actions(self, beginning_actions=None, end_actions=None, between_rows_actions=None):
        super(Setting2D, self).add_actions(beginning_actions, end_actions)
        self.__between_rows_actions.extend(between_rows_actions)

    def is_new_start(self):
        return self._idx == 0 and self.__row_idx == 0

    def get_actions(self):
        actions = []
        if self.__row_idx == len(self._list) - 1 and self._idx == len(self._list[self.__row_idx]) - 1 \
                and self._end_actions:
            actions.extend(self._end_actions)

        if self.__row_idx == 0 and self._idx == 0 and self._beginning_actions:
            actions.extend(self._beginning_actions)

        if self._idx == len(self._list[self.__row_idx]) - 1 and self.__between_rows_actions:
            actions.extend(self.__between_rows_actions)

        return actions

    def get_setting(self):
        return self._list[self.__row_idx][self._idx]

    def increment(self):
        self._idx += 1
        if self._idx == len(self._list[self.__row_idx]):
            self._idx = 0
            self.__row_idx += 1
            if self.__row_idx == len(self._list):
                self.__row_idx = 0
                self._idx = 0
                return False
        return True


class Scenario:
    def __init__(self, scenarios: dict):
        self._dict = OrderedDict()
        for setting_type, scen in scenarios.items():
            self._dict[setting_type] = Setting(scenarios[setting_type])
        if "weeks" in self._dict:
            self._dict["weeks"].add_actions(beginning_actions=[Action.REINITIALIZE_NETWORK,
                                                               Action.REINITIALIZE_OUTPUT_WRITER],
                                            end_actions=[Action.FINISH_OUTPUT_WRITING])
        self._stop = False

    def __iter__(self):
        self._stop = False
        for _, setting in self._dict.items():
            setting.init()
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration

        self._set_configuration()
        collect_beginning_actions = self._beginning()

        actions_to_take = []
        increment = True
        for key, setting in self._dict.items():
            actions_to_take.extend(setting.get_actions())
            # If the setting vector could be incremented
            # Usually this is the innermost vector
            if increment and setting.increment():
                if collect_beginning_actions:
                    increment = False
                else:
                    break
            # Iterated through all setting combinations, if it wasn't due to collecting beginning actions,
            # set the variable "collect_beginning_actions" to false.
            # This can happen if all setting arrays are single-element
            if increment and collect_beginning_actions and key == list(self._dict.keys())[-1]:
                collect_beginning_actions = False
            # Iterated through all setting combinations, not due to collecting actions
            if not collect_beginning_actions and key == list(self._dict.keys())[-1]:
                self._stop = True
        return actions_to_take

    def _set_configuration(self):
        if "network_kinds" in self._dict:
            configuration.config.set_boolean("network", "build_exact",
                                             True if self._dict["network_kinds"].get_setting() == "exact"
                                            else False)
            configuration.config.set_boolean("network", "cut_to_pieces",
                                             True if self._dict[
                                                        "network_kinds"].get_setting() == "cut_to_pieces" else False)
        if "networks" in self._dict:
            configuration.config.set("input", "network_id", str(self._dict["networks"].get_setting()))
        if "scenarios" in self._dict:
            configuration.config.set("scenario", "scenario", self._dict["scenarios"].get_setting())
        if "weeks" in self._dict:
            configuration.config.set("scenario", "week_index", str(self._dict["weeks"].get_setting()))

    def _beginning(self):
        for _, setting in self._dict.items():
            if not setting.is_new_start():
                return False
        return True


class MeterPositioningScenario(Scenario):
    def __init__(self, scenarios: dict):
        super(MeterPositioningScenario, self).__init__(scenarios)
        self._dict.pop("scenarios")
        self._dict["weeks"] = Setting(scenarios["weeks"],
                                      [Action.REINITIALIZE_OUTPUT_WRITER],
                                      [Action.FINISH_OUTPUT_WRITING, Action.SAVE_METER_ACCURACY])
        self._dict["metering_bus"] = Setting2D(None, None,
                                               [Action.REINIT_METER_PLACEMENT],
                                               [Action.FIX_MOST_ACCURATE_METER, Action.REINIT_PRECISION])
        self._dict.move_to_end("metering_bus", last=False)
        self._dict.move_to_end("weeks", last=False)
        self._dict["networks"].add_actions(beginning_actions=[Action.REINITIALIZE_NETWORK])

    def __iter__(self):
        configuration.config.set_boolean("scenario", "meter_positioning", True)
        getLogger("scenarios_iterator.MeterPositioningScenario").warning("BasicScenario is set to: "
                                                                         + configuration.config.get("scenario",
                                                                                                    "scenario").value)
        return super(MeterPositioningScenario, self).__iter__()

    def _set_configuration(self):
        configuration.config.set("scenario", "week_index", self._dict["weeks"].get_setting())
        configuration.config.set_boolean("network", "build_exact",
                                         True if self._dict["network_kinds"].get_setting() == "exact"
                                        else False)
        configuration.config.set_boolean("network", "cut_to_pieces", True if self._dict["network_kinds"].get_setting()
                                                                             == "cut_to_pieces" else False)
        configuration.config.set("input", "network_id", self._dict["networks"].get_setting())
        if self._dict["network_kinds"].is_new_start():
            if not accuracy_statistics.initialized():
                accuracy_statistics.reinitialize(network_factory())
                if configuration.config.getboolean("scenario", "metering_position_use_pv"):
                    self._dict["metering_bus"].set_settings([accuracy_statistics.get_pv_circuit()])
                else:
                    self._dict["metering_bus"].set_settings(accuracy_statistics.get_ordered_circuits())
        configuration.config.set("scenario", "meter_positioning_bus", str(self._dict["metering_bus"].get_setting()))


class HmkeScenario(Scenario):
    def __init__(self, scenarios: dict):
        super(HmkeScenario, self).__init__(scenarios)
        self._dict.pop("scenarios")
        self.__scenario = scenarios["scenarios"][0]
        self._dict["networks"].add_actions(beginning_actions=[Action.REINITIALIZE_NETWORK])

    def __iter__(self):
        configuration.config.set("scenario", "scenario", self.__scenario.value)
        configuration.config.set("scenario", "subscenario", self._dict["subscenarios"].get_setting())
        configuration.config.set_boolean("network", "build_exact", True)
        configuration.config.set_boolean("network", "cut_to_pieces", False)
        return super(HmkeScenario, self).__iter__()


class ControlledScenario(Scenario):
    def __init__(self, scenarios: dict):
        super(ControlledScenario, self).__init__(scenarios)
        self._dict.pop("network_kinds")
        self._dict["networks"].add_actions(beginning_actions=[Action.REINITIALIZE_NETWORK])

    def __iter__(self):
        return super(ControlledScenario, self).__iter__()


class ScenarioIterator:
    def __init__(self):
        self.__scenarios = scenario_factory()
        self.__scen_idx = 0
        self.__inner_idx = 0

    def __iter__(self):
        self.__scen_idx = 0
        self.__inner_idx = 0
        self.__sc_iter = iter(self.__scenarios[0])
        return self

    def __next__(self):
        if self.__scen_idx < len(self.__scenarios):
            try:
                return next(self.__sc_iter)
            except StopIteration:
                self.__scen_idx += 1
                if self.__scen_idx == len(self.__scenarios):
                    raise StopIteration
                self.__sc_iter = iter(self.__scenarios[self.__scen_idx])
                return next(self.__sc_iter)
        else:
            raise StopIteration
