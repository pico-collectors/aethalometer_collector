"""Aethalometer Data Collector

Usage:
  aethalometer --ip=<ip_or_domain> --port=<port> --storage=<directory>
  aethalometer --config=<file>
  aethalometer (-h | --help)

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import logging

import sys
from data_collecting.runner import Runner
from docopt import docopt

from aethalometer_collector.configuration import AethalometerConfiguration, \
    ConfigValueError
from aethalometer_collector.data_collector import AethalometerDataCollector
from aethalometer_collector.storage_handler import AethalometerStorageHandler


def main():

    logger = logging.getLogger('')

    #
    # Start by loading the configurations based on the user input
    #

    args = docopt(__doc__, version='0.1')

    # Loads the default configurations
    config = AethalometerConfiguration()

    if args['--config']:
        config.read(config_file=args['--config'])
    else:
        config['producer_ip'] = args['--ip']
        config['producer_port'] = args['--port']
        config['storage_directory'] = args['--storage']

    #
    # Once the configurations are set, setup the runner and execute the
    # program
    #

    try:
        runner = Runner(collector=AethalometerDataCollector(
            storage_handler=AethalometerStorageHandler(config['storage_directory']),
            producer_address=(config['producer_ip'], config['producer_port']),
            reconnect_period=config['reconnect_period'],
            message_period=config['message_period'],
        ))

    except ConfigValueError as error:
        logger.error("Error in the configuration file: %s" % error.message)
        sys.exit(1)

    runner.run()

if __name__ == '__main__':
    main()
