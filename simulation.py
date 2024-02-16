from logging import getLogger

import output_writer.estimation_param_output_writer as eow
import output_writer.meter_placement_output_writer as mow
import output_writer.network_output_writer as now
import utility.configuration as configuration
from algorithm.algorithm_factory import algorithm_factory
from algorithm.definitions import AlgorithmAim
from algorithm.validator import validator_factory
from measurement.create_measurement_factory import create_measurement_factory
from network.definitions import Network
from network.network_factory import network_factory
from network.network_kind_string import get_network_kind_string
from output_writer.output_writer import OutputWriterKind
from smart_meter_placement.accuracy_statistics import accuracy_statistics
from utility import performance as p
from utility.scenario_iterator import ScenarioIterator, Action
from utility.utils import get_number_of_slots_per_week, get_current_time_string


def _scenario_string():
    return "Simulation starts for week no. '" + configuration.config.get("scenario", "week_index") + \
        "', scenario: '" + configuration.config.get("scenario", "scenario").value + "'" + \
        ", network: '" + str(configuration.config.get("input", "network_id").value) + "', " + \
        get_network_kind_string() + \
        (", meter positioning, bus no. " + str(configuration.config.getint("scenario", "meter_positioning_bus")) if
         configuration.config.getboolean("scenario", "meter_positioning") else "") + \
        (f", PV scenario: {configuration.config.get_scenario()} with sub-scenario:"
         f" {configuration.config.get_subscenario()}" if configuration.config.is_pv_scenario() else "")


class Simulation(object):
    def __init__(self):
        self._logger = getLogger("simulation")
        self.__step_count = get_number_of_slots_per_week()

        network = configuration.config.get_network()
        # Multi-unit run is currently only defined for pilot locations
        self._multi_unit_run = configuration.config.multi_unit_run()
        self._net = None if self._multi_unit_run else network_factory()
        self._measurement_factory = create_measurement_factory()
        self._measurement_factory.set_network(network, self._net)
        self._simulator = algorithm_factory(configuration.config.get_generator("simulation"), self._net,
                                            self._measurement_factory,
                                            aim=AlgorithmAim.MAIN_SIMULATION)
        self._performance_measurer = p.PerformanceMeasurer()
        self._const_consumption_scenarios = configuration.config.get("multiple_run", "constant_consumption_scenarios",
                                                                     fallback=list())
        self._output_writers = dict()

        if configuration.config.getboolean("output", "save_output"):
            self._output_writers[OutputWriterKind.SIMULATION] = now.NetworkOutputWriter(self._net,
                                                                                        data_type=configuration.config.get_generator(
                                                                                            "simulation"),
                                                                                        name="simulation")

        if network == Network.PILOT:
            self._output_writers[OutputWriterKind.ESTIMATION_PARAMS] = eow.EstimationParamOutputWriter(
                self._simulator.performance_indicators)

        self._output_writers[OutputWriterKind.METER_PLACEMENT] = mow.MeterPlacementOutputWriter() if \
            not configuration.config.getboolean("scenario",
                                                "metering_position_use_pv") else \
            mow.MeterPlacementOutputWriterPvScenario()

    def _init_output_writing(self, **kwargs):
        for name, writer in self._output_writers.items():
            writer.initialize(multi_unit_run=self._multi_unit_run, net=self._net, **kwargs)

    def _init_network(self):
        self._net = network_factory()
        self._measurement_factory.set_network(configuration.config.get_network(), self._net)
        self._simulator.initialize(self._net)

    def _prepare_for_simulation(self):
        self._simulator.set_measurements()
        self._performance_measurer.reset()

    def _step_auxiliary(self, i):
        pass

    def _register_results(self, i):
        for name, writer in self._output_writers.items():
            writer.write_step()
            writer.calculate()

    def _finish_simulation(self):
        pass

    def _finish_output_writing(self):
        for name, writer in self._output_writers.items():
            writer.write_final()
            writer.save()

    def run(self):
        if self._multi_unit_run:
            # Start iterating different scenarios
            for scenario in ScenarioIterator():
                self.do_actions_before(scenario)
                self.run_unit()
                self.do_actions_after(scenario)
        else:
            self._init_output_writing()
            self.run_unit()
            self._finish_output_writing()

    def run_unit(self):
        if self._multi_unit_run:
            self._logger.info(_scenario_string())

        self._prepare_for_simulation()

        for i in range(0, self.__step_count):
            self._performance_measurer.start()
            success = False
            try:
                # Skip simulation for the simulations steps following the first
                self._step_auxiliary(i)
                if self._multi_unit_run and\
                        configuration.config.get_scenario().value in self._const_consumption_scenarios and i > 0:
                    success = True
                else:
                    success = self._simulator.step(i)
            except Exception as e:
                self._logger.error(f"An error happened during the simulation '{e}'")
                break
            finally:
                self._performance_measurer.stop()

            if success:
                self._register_results(i)

            self._logger.info(get_current_time_string(i))

        # Write output
        self._finish_simulation()

    def do_actions_before(self, to_do):
        if Action.REINITIALIZE_NETWORK in to_do:
            self._init_network()

        if Action.REINITIALIZE_OUTPUT_WRITER in to_do:
            self._init_output_writing()

    def do_actions_after(self, to_do):
        if Action.SAVE_METER_ACCURACY in to_do:
            accuracy_statistics.add_accuracy()

        if Action.FIX_MOST_ACCURATE_METER in to_do:
            accuracy_statistics.fix_most_accurate_meter()

        if Action.FINISH_OUTPUT_WRITING in to_do:
            self._finish_output_writing()

        if Action.REINIT_METER_PLACEMENT in to_do:
            accuracy_statistics.reinitialize(self._net)

        if Action.REINIT_PRECISION in to_do:
            accuracy_statistics.reinitialize_accuracy()


class SimulationWithValidation(Simulation):
    def __init__(self):
        super().__init__()
        self._validation_network = None if self._multi_unit_run else self._net
        self._output_writers[OutputWriterKind.VALIDATION] = now.NetworkOutputWriter(self._validation_network,
                                                                                    data_type=configuration.config.get_generator(
                                                                                        "validator"),
                                                                                    name="validation")

        if configuration.config.getboolean("output", "save_validation_simulation_difference", fallback=False):
            self._output_writers[OutputWriterKind.DIFFERENCE] = \
                now.DifferenceNetworkOutputWriter(validator_network=self._validation_network,
                                                  simulator_network=self._net,
                                                  name="difference")
        else:
            self._logger.warning("Validation and simulation difference output saving is switched off.")
        self.__validation = validator_factory(configuration.config.get("validation", "validation_source"),
                                              configuration.config.get_generator("validator"), self._validation_network,
                                              self._measurement_factory, aim=AlgorithmAim.VALIDATION)

    def _init_network(self):
        super(SimulationWithValidation, self)._init_network()
        self._validation_network = self._net
        self.__validation.initialize(self._validation_network)

    def _init_output_writing(self):
        for kind, writer in self._output_writers.items():
            network = self._net if kind == OutputWriterKind.SIMULATION else \
                (self._validation_network if kind == OutputWriterKind.VALIDATION else None)
            writer.initialize(multi_unit_run=self._multi_unit_run, net=network, simulator_network=self._net,
                              validator_network=self._validation_network)

    def _prepare_for_simulation(self):
        super()._prepare_for_simulation()
        self.__validation.set_measurements()

    def _step_auxiliary(self, i):
        super()._step_auxiliary(i)
        self.__validation.step(i)

    def _finish_simulation(self):
        super()._finish_simulation()

        self._logger.info(f"Average step time: {self._performance_measurer.get_average():.4f} s")
