import logging
from re import match

from numpy import max, min, isclose
from numpy.linalg import eig
from pandapower import create_measurement
from pandapower.estimation import ALGORITHM_MAPPING, StateEstimation
from pandapower.estimation.ppc_conversion import _initialize_voltage
from pandas import DataFrame

import utility.configuration as configuration
from algorithm.algorithm import Algorithm
from algorithm.definitions import AlgorithmType, AlgorithmAim
from measurement.definitions import ControlledScenario


class PerformanceIndicators:
    def __init__(self):
        self.Gm_max_eigenvalue = 0
        self.Gm_min_eigenvalue = 0
        self.num_iterations = 0
        self.error = 0

    @staticmethod
    def names_to_data_frame():
        return DataFrame(["number of iterations", "error", "gain max eigenvalue", "gain min eigenvalue"])

    def to_data_frame(self):
        return DataFrame([self.num_iterations, self.error, self.Gm_max_eigenvalue, self.Gm_min_eigenvalue])


class _EstimationStreamFilter(logging.Filter):
    """Filter class for parsing the pp.StateEstimation object's log stream, and saving the number of iterations from it.
    Serves as an API to the StateEstimation.
    This is a workaround used to prevent modifying the pandapower libraries.
    """

    def __init__(self, performance_indicators, level):
        super().__init__()
        self.performance_indicators = performance_indicators
        self.__level = level
        self.__logger = logging.getLogger("estimation")

    def filter(self, record):
        if record.getMessage().endswith('iterations)'):
            m = match(r".*\s\((\d+) iterations\)", record.getMessage())
            if m:
                try:
                    self.performance_indicators.num_iterations = int(m.group(1))
                except Exception:
                    self.__logger.error("Cannot convert log message to iteration count.")
                    self.performance_indicators.num_iterations = None
        elif record.getMessage().startswith('Current error:'):
            m = match(r"Current error: (\d+\.\d+).*", record.getMessage())
            if m:
                try:
                    self.performance_indicators.error = float(m.group(1))
                except Exception:
                    self.__logger.error("Cannot convert log message to current error.")
                    self.performance_indicators.error = None
        return record.levelno >= self.__level


class Estimator(Algorithm):
    name = "StateEstimation"
    kind = AlgorithmType.ESTIMATION

    def __init__(self, net=None, measurement_factory=None, aim=AlgorithmAim.MAIN_SIMULATION):
        super().__init__(net, measurement_factory, aim)
        self.performance_indicators = PerformanceIndicators()
        self.__iteration_number_filter = _EstimationStreamFilter(self.performance_indicators, logging.INFO)
        self._logger.addFilter(self.__iteration_number_filter)
        self.__algorithm = configuration.config.get("algorithm", "algorithm")
        self.__estimator = None if self.__algorithm == "wls" else ("lav" if self.__algorithm == "lp" else
                                                                   configuration.config.get("algorithm", "estimator",
                                                                                            fallback=None))
        self._logger.info(f"Using algorithm: {self.__algorithm}")
        self.__calculate_voltage_angles = configuration.config.getboolean("algorithm", "calculate_voltage_angles")
        self.__state_estimator = None

    def step(self, idx=None):
        self.__add_measurements()

        try:
            if idx == 0:  # Initialize estimation for first step
                self.__estimate(self._net, algorithm=self.__algorithm, init="flat",
                                calculate_voltage_angles=self.__calculate_voltage_angles,
                                zero_injection="auto", estimator=self.__estimator, a=3)

            # Run the state estimation
            success = self.__estimate(self._net, algorithm=self.__algorithm, init="flat",
                                      calculate_voltage_angles=self.__calculate_voltage_angles, zero_injection="auto",
                                      estimator=self.__estimator, a=3)
        except Exception as e:
            self._logger.error(f"State estimation error {e}")
            return False

        return success

    # Adds the measurements to the network
    def __add_measurements(self, drop_measurements=True):
        # Delete previous measurements from the network
        if drop_measurements:
            self._net.measurement.drop(self._net.measurement.index, inplace=True)

        # Add new measurements
        for measurement in self._measurements:
            measurement_value = measurement.get_next_measurement()
            std_dev = measurement.get_std_dev()
            assert not isclose(std_dev, 0.0, atol=1e-9), "Measurement deviation '" + str(
                std_dev) + "' is (almost) zero!"
            create_measurement(self._net, meas_type=measurement.type, element_type=measurement.element_type,
                               value=measurement_value, std_dev=std_dev,
                               element=measurement.element_idx, side=measurement.element_side, check_existing=True,
                               name=measurement.name)

        if configuration.config.get_scenario() == ControlledScenario.SC_1_NON_CONTROLLED:
            controlled_bus = self._net.controller.object[0].controlled_bus
            if not any((self._net.measurement.element_type == "bus") &
                       (controlled_bus == self._net.measurement.index) &
                       (self._net.measurement.measurement_type == "p")):
                create_measurement(self._net, meas_type="p", element_type="bus",
                                   value=0, std_dev=0.01,
                                   element=controlled_bus, side=None,
                                   check_existing=True, name="zero_inj")

    def __estimate(self, net, algorithm='wls',
                   init='flat', tolerance=1e-6, maximum_iterations=5000,
                   calculate_voltage_angles=True,
                   zero_injection='aux_bus', fuse_buses_with_bb_switch='all', **opt_vars):
        """Copied from pandapower.state_estimation.estimate for handling the StateEstimation object's members
            separately, and for saving them."""
        if algorithm not in ALGORITHM_MAPPING:
            raise UserWarning(f"Algorithm {algorithm} is not a valid estimator")

        se = StateEstimation(net, tolerance, maximum_iterations, algorithm=algorithm,
                             logger=self._logger)
        v_start, delta_start = _initialize_voltage(net, init, calculate_voltage_angles)
        success = se.estimate(v_start=v_start, delta_start=delta_start,
                              calculate_voltage_angles=calculate_voltage_angles,
                              zero_injection=zero_injection,
                              fuse_buses_with_bb_switch=fuse_buses_with_bb_switch, **opt_vars)

        if success and self.__algorithm == "wls":
            v_eig, _ = eig(se.solver.Gm)
            self.performance_indicators.Gm_max_eigenvalue = max(v_eig)
            self.performance_indicators.Gm_min_eigenvalue = min(v_eig)

        return success
