from logging import getLogger

from algorithm.definitions import AlgorithmType, AlgorithmAim


class Algorithm:
    name = "Algorithm"
    kind = AlgorithmType.INVALID

    def __init__(self, net=None, measurement_factory=None, aim=AlgorithmAim.INVALID):
        assert aim != AlgorithmAim.INVALID, "Algorithm aim has not been properly set!"
        self._net = net
        self._measurement_factory = measurement_factory
        self._measurements = None
        self._logger = getLogger(self.name)
        self._aim = aim

    def initialize(self, net=None):
        self._net = net

    def set_measurements(self):
        self._measurements = self._measurement_factory.create_measurements(for_validation=
                                                                           (self._aim == AlgorithmAim.VALIDATION))

    def get_measurements(self):
        return self._measurements

    def step(self, idx=None):
        pass
