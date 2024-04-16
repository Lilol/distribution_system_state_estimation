from algorithm.algorithm import Algorithm
from algorithm.definitions import AlgorithmType, AlgorithmAim


class NoAlgorithm(Algorithm):
    name = "NoAlgorithm"
    kind = AlgorithmType.NONE

    def __init__(self, net=None, measurement_factory=None, aim=AlgorithmAim.VALIDATION):
        super().__init__(net, measurement_factory, aim)

    def set_measurements(self):
        self._measurements = self._measurement_factory.create_measurements(for_validation=
                                                                           (self._aim == AlgorithmAim.VALIDATION))

    def get_measurements(self):
        return self._measurements

    def step(self, idx=None):
        return True