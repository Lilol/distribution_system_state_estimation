import utility.configuration as configuration
from measurement.besnica.besnica_measurement_factory import BesnicaMeasurementFactory
from measurement.controlled.controlled_scen_measurement_factory import ControlledScenarioMeasurementFactory
from measurement.definitions import ControlledScenario, PvScenario, BasicScenario, SmartMeterScenario
from measurement.medium_voltage.measurement_factory import MediumVoltageMeasurementFactory
from measurement.pilot.pilot_measurement_factory_for_basic_scenario import PilotMeasurementFactoryForBasicScenarios
from measurement.pilot.pilot_measurement_factory_for_smart_meter_measurements import \
    PilotMeasurementFactoryForSmartMeterMeasurements
from measurement.pilot.pv_measurement_factory import PilotMeasurementFactoryForPvScenario
from network.definitions import Network, NetworkId


def create_measurement_factory():
    network = configuration.config.get_network()
    if network in (Network.BESNICA, Network.BESNICA_REDUCED):
        return BesnicaMeasurementFactory()

    scenario = configuration.config.get_scenario()
    if network == Network.MEDIUM_VOLTAGE:
        network_id = configuration.config.get_network_id()
        assert network_id == NetworkId.ID_220018, f"Invalid network id {network_id} used with medium voltage network"
        return MediumVoltageMeasurementFactory()
    elif type(scenario) == ControlledScenario:
        assert network == Network.CONTROLLED, f"Invalid network type '{network.value}' used with Controlled scenario"
        return ControlledScenarioMeasurementFactory()
    else:
        assert network == Network.PILOT, f"Invalid network type '{network.value}' used with pilot scenario"
        if type(scenario) == PvScenario or scenario == BasicScenario.PV:
            return PilotMeasurementFactoryForPvScenario()
        elif type(scenario) == SmartMeterScenario:
            return PilotMeasurementFactoryForSmartMeterMeasurements()
        else:
            return PilotMeasurementFactoryForBasicScenarios()
