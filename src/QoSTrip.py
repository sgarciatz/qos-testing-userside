import datetime
import sqlite3

class QoSTrip():


    def __init__(self,
                 ms_id: str,
                 host_id: str,
                 server_id: str,
                 request_send_time: str,
                 request_payload_size: int,
                 request_arrival_time: str,
                 response_send_time: str,
                 response_payload_size: int) -> None:

        self.ms_id: str = ms_id
        self.host_id: str = host_id
        self.server_id: str = server_id
        self.request_send_time: str = request_send_time
        self.request_payload_size: int = request_payload_size
        self.request_arrival_time: str = request_arrival_time
        self.response_send_time: str = response_send_time
        self.response_payload_size: int = response_payload_size
        self.response_arrival_time: str = str(datetime.datetime.now())


    def insert_QoSTrip(self, experiment_id: str) -> None:

        """Insert a QoSTrip object into the database"""
