import configparser
import os
import sys
from collections import OrderedDict
from logging import getLogger

from data_extractor.definitions import GeneratorType
from measurement.definitions import BasicScenario, ControlledScenario, PvScenario, subscenario, SmartMeterScenario
from network.definitions import Network, NetworkId, network_name


class ConfigurationManager:
    def __init__(self, config_filename=os.path.join("..", "config", "config.ini")):
        self.config = configparser.RawConfigParser(allow_no_value=True,
                                                   interpolation=configparser.ExtendedInterpolation())
        self.config.read_file(open(config_filename))
        self.__logger = getLogger("config")

    def get(self, section, key, fallback=None):
        if section == "multiple_run" and key == "scenarios":
            return self.__get_scenarios()

        if section == "input" and key == "network_id":
            return self.get_network_id()

        if section == "scenario" and key == "scenario":
            return self.get_scenario()

        try:
            value = self.config.get(section, key, fallback=fallback)
        except Exception:
            raise KeyError(f"Section '{section}', key '{key}' not found in configuration")
        if value is None:
            raise KeyError(f"Section '{section}', key '{key}' not found in configuration")

        str_list = value.strip('][').replace(' ', ',').split(',')
        if len(str_list) > 1:
            return str_list
        else:
            return value

    def set(self, section, key, value):
        self.config.set(section, key, value)

    def set_boolean(self, section, key, value):
        boolean_str = 'True' if value else 'False'
        self.config.set(section, key, boolean_str)

    def get_generator(self, aim):
        assert aim in ("simulation", "validator"), "Aim must be one of the two: simulation, validator"
        generator = self.get("algorithm", aim)
        try:
            return GeneratorType(generator)
        except TypeError:
            raise TypeError(
                f"Unknown generator type: {generator}\nSet[algorithm]\n{aim}=\n in the config file.")

    def getboolean(self, section, key, fallback=None):
        return self.config.getboolean(section, key, fallback=fallback)

    def getint(self, section, key, fallback=None):
        return self.config.getint(section, key, fallback=fallback)

    def getfloat(self, section, key, fallback=None):
        return self.config.getfloat(section, key, fallback=fallback)

    def has_option(self, section, option):
        return self.config.has_option(section, option)

    def multi_unit_run(self):
        return self.config.getboolean("multiple_run", "on")

    def get_scenario(self):
        from_config = self.config.get("scenario", "scenario")
        try:
            return BasicScenario(from_config)
        except:
            pass
        try:
            return PvScenario(from_config)
        except:
            pass
        try:
            return ControlledScenario(from_config)
        except:
            pass
        try:
            return SmartMeterScenario(from_config)
        except Exception as e:
            raise e

    def get_subscenario(self):
        return subscenario[self.get_scenario()](self.config.get("scenario", "subscenario"))

    def is_pv_scenario(self):
        return type(self.get_scenario()) == PvScenario

    def get_network(self):
        return Network(self.config.get("scenario", "location"))

    def get_location_name(self):
        return network_name[self.get_network_id()]

    def get_network_id(self, section="input", key="network_id"):
        return NetworkId(self.getint(section, key))

    def __get_scenarios(self):
        if not self.multi_unit_run():
            return []

        main_sc = self.get_scenario()

        i = 1
        scenarios = dict()
        while self.has_option("multiple_run", f"scenario_{i}"):
            raw_string = self.config.get("multiple_run", f"scenario_{i}")
            split_str = raw_string.strip('[]').replace('] [', '][').split('][')
            try:
                scenario = split_str[0].replace(' ', ',').split(',')
                week_indices = split_str[1].replace(' ', ',').split(',')
                if len(split_str) > 2:
                    networks = split_str[2].replace(' ', ',').split(',')
                else:
                    networks = str(self.get_network_id().value)
                if len(split_str) > 3:
                    exact = split_str[3].replace(' ', ',').split(',')
                else:
                    exact = self.config.getboolean("network", "build_exact")

                if "all" in week_indices:
                    if type(main_sc) == ControlledScenario:
                        week_indices = [0]
                    else:
                        week_indices = [str(i) for i in range(1, 27)]
                if "all" in scenario:
                    if type(main_sc) == ControlledScenario:
                        scenario = [ControlledScenario.SC_1_NON_CONTROLLED.value,
                                    ControlledScenario.SC_2_CONTROLLED.value,
                                    ControlledScenario.SC_3_CONTROLLED_WITH_PSEUDO_MEASUREMENTS.value]
                    else:
                        scenario = ["1", "1m", "2", "2m", "2mm"]
                if "all" in networks:
                    if type(main_sc) == ControlledScenario:
                        networks = [str(NetworkId.ID_99999.value), str(NetworkId.ID_23427.value)]
                    else:
                        networks = [str(p.value) for p in NetworkId if
                                    p not in (NetworkId.ID_99999, NetworkId.ID_23427)]
                if "all" in exact:
                    exact = ["exact", "closest", "cut_to_pieces"]
                scenarios[i] = OrderedDict({"weeks": week_indices, "network_kinds": exact, "networks": networks,
                                            "scenarios": scenario})
            except Exception as e:
                self.__logger.error("Config is unable to parse scenario specifier, error occurred.")
                raise e
            else:
                i = i + 1
        return scenarios


config_file = sys.argv[2] if len(sys.argv) >= 3 else os.path.join('config', 'config.ini')
config = ConfigurationManager(config_filename=config_file)
