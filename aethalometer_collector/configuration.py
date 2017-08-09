import configparser
from logging.config import fileConfig
from pkg_resources import resource_filename, Requirement


# region Transformation functions

def ip_port(port: str) -> int:
    """
    Parses a port in string format, returning the corresponding port as
    an integer. Raises a ValueError if the port is not valid.
    """
    port = int(port)

    if 0 < port < 65536:
        raise ValueError("The port must be an integer value between 0 and "
                         "65536 (exclusive)")

    return port


def positive_float(value: str) -> float:
    """
    Converts the specified value to a float if the value is positive.

    :param value: the value to convert to a float
    :return: float value
    :raise ValueError: if the value is not a float or is a non-positive float
    """
    value = float(value)

    if value <= 0:
        raise ValueError()

    return value

# endregion


class AethalometerConfiguration:

    # Resource for the default configurations for the loggers
    LOGS_CONF_FILE = resource_filename(
        Requirement.parse("aethalometer_collector"),
        'aethalometer_collector/logs.ini')

    # Resource for the default configuration file
    DEFAULT_CONF_FILE = resource_filename(
        Requirement.parse("aethalometer_collector"),
        'aethalometer_collector/default.ini')

    # This dictionary stores the configuration keys
    # For each key it stores the section where the key is placed and the
    # transformation function to transform the string value into the required
    # value format (see transformation functions below)
    config_keys = {
        'reconnect_period':     ('base', positive_float),
        'message_period':       ('base', positive_float),
        'producer_ip':          ('aethalometer', str),
        'producer_port':        ('aethalometer', ip_port),
        'storage_directory':    ('aethalometer', str),
    }

    def __init__(self):
        """
        Initializes the configuration with the default values defined in the
        'default.ini' file.
        """
        self._config = configparser.ConfigParser()

        # Load the default configurations for the loggers
        fileConfig(self.LOGS_CONF_FILE)

        # Load the default configurations
        self.read(self.DEFAULT_CONF_FILE)

    def read(self, config_file):
        """
        Reads configurations from some configuration file. The values defined
        in the specified file will override the current values.

        :param config_file: the path to the config file to be read
        :raise NotFoundError: if the specified config file does not exist
        """
        with open(config_file) as file:
            self._config.read_file(file)

    def __getitem__(self, config_key):
        """
        Returns the config value for the specified config key. The value is
        returned in the required format (as specified in the config_key
        dictionary).

        :raise KeyError: if the specified key is not supported by this
        configuration
        """
        section, transform = self.config_keys[config_key]
        return transform(self._config[section][config_key])

    def __setitem__(self, key, value):
        section, transform = self.config_keys[key]
        self._config[section][key] = value
