import pandapower as pp
from numpy import multiply

import utility.configuration as configuration
from algorithm.algorithm import Algorithm
from algorithm.definitions import AlgorithmType, AlgorithmAim
from measurement.definitions import ControlledScenario
from network.definitions import Network, NetworkId


def _distribute_power_across_phases(load, measurement):
    return multiply([load.p_a_mw, load.p_b_mw, load.p_c_mw], measurement / sum([load.p_a_mw, load.p_b_mw, load.p_c_mw]))


class Loadflow(Algorithm):
    """This class is responsible for storing information collected from the state estimation process, its validation,
         and extracting measures (e.g. the accuracy of the algorithm) from the collected data."""

    name = "Loadflow"
    kind = AlgorithmType.LOADFLOW

    def __init__(self, net=None, measurement_factory=None, aim=AlgorithmAim.VALIDATION):
        super().__init__(net, measurement_factory, aim)
        if configuration.config.get_network() in (Network.BESNICA, Network.BESNICA_REDUCED):
            self._net.bus.vn_kv = self._net.bus.vn_kv * configuration.config.getfloat(
                "physics", "transformer_voltage_increase_factor", fallback=1)
        self._init = configuration.config.get("algorithm", "init_pp")

    def step(self, idx=None):
        self._apply_measurements_to_net(idx)

        try:
            if idx == 0:  # Initialize the power flow at first step.at
                self.run_powerflow(init="dc")

            # Run power flow for validation
            self.run_powerflow(init="dc")
        except:
            return False
        else:
            return True

    def run_powerflow(self, init="dc"):
        try:
            pp.runpp(self._net, init=init)
        except Exception as e:
            self._logger.error(f"Loadflow did not converge: {e}")

    def _apply_measurements_to_net(self, idx):
        self.__reset_network_loads()
        for measurement in self._measurements:
            if measurement.element_type == "bus" and measurement.type in ("p", "q"):
                measurement_value = measurement.get_measurement_value(idx)
                try:
                    if measurement.element_type == "bus":
                        bus = measurement.element_idx
                    else:
                        if isinstance(measurement.element_side, int):
                            bus = measurement.element_side
                        else:
                            bus = self._net[measurement.element_type].loc[measurement.element_idx,
                            f"{measurement.element_side}_bus"]
                    element = "load" if measurement_value >= 0 else "sgen"
                    element_idx = self._net[f"{element}"][self._net[f"{element}"].bus == bus].index[0]
                except IndexError:
                    if self._net.ext_grid.bus[0] == measurement.element_idx:
                        self._logger.warning(f"No bus with index {measurement.element_idx}, this bus has an external"
                                             f" grid.")
                    else:
                        self._logger.info(f"Unknown {measurement.element_type} with index"
                                          f" '{measurement.element_idx}'.")
                    continue
                else:
                    # Save the values for power flow simulations
                    if measurement.type == "p":
                        property_to_set = 'p_mw'
                    else:
                        property_to_set = 'q_mvar'

                    self._net[f"{element}"].at[element_idx, property_to_set] += abs(measurement_value)

    def __reset_network_loads(self):
        self._net.load.p_mw = 0.0
        self._net.load.q_mvar = 0.0
        self._net.sgen.p_mw = 0.0
        self._net.sgen.q_mvar = 0.0


class ControlledLoadflow(Loadflow):
    def __init__(self, net=None, measurement_factory=None, aim=AlgorithmAim.VALIDATION):
        super().__init__(net, measurement_factory, aim)

    def run_powerflow(self, init="dc"):
        run_control = self.__run_control()
        try:
            pp.runpp(self._net, init=init, run_control=run_control)
        except Exception as e:
            self._logger.error(f"Loadflow did not converge: {e}")

    def _apply_measurements_to_net(self, idx):
        super(ControlledLoadflow, self)._apply_measurements_to_net(idx)
        ext_grid_measurement = self._measurements.get_measurement("V_ext_grid")
        self._net.ext_grid.at[0, "vm_pu"] = ext_grid_measurement.get_measurement_value(idx)
        controller_measurement = self._measurements.get_measurement("V_controller").get_measurement_value(idx)
        if configuration.config.get_scenario() == ControlledScenario.SC_1_NON_CONTROLLED:
            if not any(self._net.gen.bus == self._net.controller.object[0].controlled_bus):
                pp.create_gen(self._net, self._net.controller.object[0].controlled_bus, vm_pu=1, p_mw=0.)
            self._net.gen.loc[
                self._net.gen.bus == self._net.controller.object[0].controlled_bus, "vm_pu"] = controller_measurement
        try:
            self._net.controller.object[0].vm_set_pu = controller_measurement
        except KeyError:
            return

    @staticmethod
    def __run_control():
        return configuration.config.get_scenario() != ControlledScenario.SC_1_NON_CONTROLLED or \
            configuration.config.get_network_id() == NetworkId.ID_220018 and \
            configuration.config.getboolean("network.medium_voltage", "use_controller")
