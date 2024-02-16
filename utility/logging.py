import logging
from datetime import date
from os import makedirs
from os.path import join, exists

import utility.configuration as configuration


def init_logger():
    # create logger
    loggers = list()
    loggers.append(logging.getLogger('main'))
    loggers.append(logging.getLogger('create_network'))
    loggers.append(logging.getLogger('performance'))
    loggers.append(logging.getLogger('simulation'))
    loggers.append(logging.getLogger('measurements'))
    loggers.append(logging.getLogger('output_writer.network'))
    loggers.append(logging.getLogger('output_writer.estimation_params'))
    loggers.append(logging.getLogger('output_writer.data_extractor'))
    loggers.append(logging.getLogger('output_writer.meter_placement'))
    loggers.append(logging.getLogger('loadflow'))
    loggers.append(logging.getLogger('estimation'))
    loggers.append(logging.getLogger('load_measurement_pairing'))
    loggers.append(logging.getLogger('config'))
    loggers.append(logging.getLogger('smart_meter_placement.globals.AccuracyStatistics'))
    loggers.append(logging.getLogger('smart_meter_placement.checkpoint_restart'))
    loggers.append(logging.getLogger('scenarios_iterator.MeterPositioningScenario'))

    # Remove already existing handlers
    for logger in loggers:
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])

        logger.setLevel(logging.DEBUG)

        log_path = configuration.config.get("paths", "log_path")
        makedirs(log_path, exist_ok=True)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(join(log_path,
                                      configuration.config.get("output", "log_file")
                                      + "_" + date.today().strftime("%y%m%d") + ".txt"))
        fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

    return loggers
