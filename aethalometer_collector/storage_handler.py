import logging

import os

from data_collecting.data_collector import CorruptedDataError
from data_collecting.data_handler import DataHandler
from data_collecting.exceptions import UnrecoverableError

logger = logging.getLogger("storage_handler")


class AethalometerStorageHandler(DataHandler):
    """
    Stores data lines inside files with the name BCYYMMDD.CSV, where DD is
    the day of the data line, MM is the month of the line, and YY is the year.
    The files are stored in the store_dir and moved to the backup_dir once
    a new file is created.
    """

    _DELIMITER = ','

    def __init__(self, storage_directory: str):
        self.storage_directory = storage_directory

    def process(self, data: str):
        """
        This method is invoked by the protocol after a new data item is
        received. The parameter 'data' is already decoded and should contain
        a string line (without the end line characters) to be processed.

        :param data: the data line to be processed
        """
        # Ignore emtpy items
        if data == "":
            return

        values = data.split(self._DELIMITER)

        # There must be at least 3 values: the date, time, and a data value
        if len(values) < 3:
            raise CorruptedDataError("Data line has less than three values")

        # Obtain the filename based on the date of the data line
        filename = generate_filename(date_value=values[0].strip())

        try:
            # Append the new data line to the output file
            # Create the output file if it does not exist
            output_path = os.path.join(self.storage_directory, filename)
            with open(output_path, "a") as out_file:
                out_file.write(data)
                out_file.write('\n')

        except OSError as error:
            raise UnrecoverableError("Failed to access the storage directory: "
                                     "%s" % str(error))

        logger.info("Wrote a new data line to '%s'" % filename)
        logger.debug("line: %s" % data)


# We use a map here instead of using the strptime from the datetime
# library because this library uses the system locale to determine the
# name of the months. For our purposes we do not want to depend of the
# system locale settings to convert the string months to integer values
_month_to_int = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def generate_filename(date_value: str) -> str:
    """
    Generates the name of the output file for a certain data item based
    on its date value.
    """
    try:
        day, month, year = date_value.replace("\"", "").split("-")
        day = int(day)
        month = _month_to_int[month.lower()]
        year = int(year) % 100

    except (KeyError, ValueError):
        raise CorruptedDataError("The date value '%s' from the data line is "
                                 "invalid")

    return "BC%02d%02d%02d.csv" % (day, month, year)
