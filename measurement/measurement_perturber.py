from logging import getLogger

from numpy import random, shape

import utility.configuration as configuration


# This class is responsible for generating randomized noise (perturbation) for the measurements.
class MeasurementPerturber:
    __error_v_pu = 0.005
    __error_angle_deg = 0.01

    # distribution: uniform, normal
    # seed_value: 'time': the seed is the current time, other int value: the seed can be provided manually for
    # reproducibility
    def __init__(self, distribution="normal"):
        self.__random = random.default_rng(configuration.config.getint("DEFAULT", "seed"))
        self.__distribution_type = distribution
        self.__logger = getLogger("measurement_perturber")

    def __get_perturbation(self, error, measurement):
        if self.__distribution_type == "normal":
            noise = self.__random.normal(0, error / 3, shape(measurement))
        elif self.__distribution_type == "uniform":
            dev = error
            noise = self.__random.uniform(low=-dev, high=dev, size=shape(measurement))
        else:
            raise ValueError(f"Unknown distribution type:{self.__distribution_type}")
        self.__logger.debug(f"Noise values: {str(noise)}")
        return measurement + noise

    def perturb_measurement(self, measurement, data_kind):
        if "angle" in data_kind:
            return self.__get_perturbation(self.__error_angle_deg, measurement)
        elif "voltage" in data_kind:
            return self.__get_perturbation(self.__error_v_pu, measurement)
        return measurement
