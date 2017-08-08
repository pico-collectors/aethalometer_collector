from data_collecting.connection import Connection
from data_collecting.data_collector import BaseDataCollector

from aethalometer_collector.storage_handler import AethalometerStorageHandler


class AethalometerDataCollector(BaseDataCollector):

    def __init__(self, storage_handler: AethalometerStorageHandler,
                 producer_address, reconnect_period, message_period):

        super().__init__(producer_address, reconnect_period, message_period)
        self._storage_handler = storage_handler

    def on_data_received(self, connection: Connection, data: bytes):
        data_item = data.decode()
        self._storage_handler.process(data_item)
