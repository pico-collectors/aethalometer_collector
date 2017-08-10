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

import os
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

        try:
            config.read(config_file=args['--config'])

        except FileNotFoundError:
            logger.error("Configuration file '%s' does not exist" %
                         args['--config'])
            sys.exit(1)

    else:
        config['ip'] = args['--ip']
        config['port'] = args['--port']
        config['storage_directory'] = args['--storage']

    # Make sure the storage directory exists
    if not os.path.isdir(config['storage_directory']):
        logger.error("Storage directory does not exist: %s" %
                     config['storage_directory'])
        sys.exit(1)

    #
    # Once the configurations are set, setup the runner and execute the
    # program
    #

    # Store the Process ID
    with open(config['pid_file'], "w") as file:
        file.write(str(os.getpid()))

    try:
        runner = Runner(collector=AethalometerDataCollector(
            AethalometerStorageHandler(config['storage_directory']),
            producer_address=(config['ip'], config['port']),
            reconnect_period=config['reconnect_period'],
            message_period=config['message_period'],
            max_msg_delay=config['max_message_delay']
        ))

    except ConfigValueError as error:
        logger.error("Error in the configuration file: %s" % error.message)
        sys.exit(1)

    runner.run()

if __name__ == '__main__':
    main()
