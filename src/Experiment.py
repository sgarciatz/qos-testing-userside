import sqlite3
import ipaddress
import requests
import os
import datetime
import statistics
from QoSRequestWithPayload import QoSRequestWithPayload
from QoSTrip import QoSTrip


class Experiment(object):


    """This class represents an Experiment. It is in charge of storing
    the results in the data base.

    Attributes:
    - id : str = A name for the experiment
    - description: str = A text description to remember the objective
      of the experiment.
    """

    def __init__(self, exp_id, exp_description, db_conn):

        """Create an Experiment object"""

        self.exp_id = exp_id
        self.exp_description = exp_description

        self.conn = db_conn
        self.cursor = self.conn.cursor()


    def create_experiment(self):

        """Create a new entry in the experiment table and creates if it
        does not exist.
        """

        self.cursor.execute((
            "CREATE TABLE IF NOT EXISTS experiment"
            "(id TEXT PRIMARY KEY,"
            "description TEXT)"))

        self.cursor.execute((
            "CREATE TABLE IF NOT EXISTS microservice_trip"
            "(host_id TEXT,"
            "server_id TEXT,"
            "ms_id TEXT,"
            "experiment_id TEXT,"
            "request_send_time DATETIME,"
            "request_arrival_time DATETIME,"
            "request_payload_size INTEGER,"
            "response_send_time DATETIME,"
            "response_arrival_time DATETIME,"
            "response_payload_size INTEGER,"
            "PRIMARY KEY (host_id, ms_id, server_id, request_send_time),"
            "FOREIGN KEY (experiment_id) REFERENCES experiment(id))"))

        self.cursor.execute((
            "INSERT INTO experiment VALUES ("
            f"\"{self.exp_id}\","
            f"\"{self.exp_description}\")"))

        self.conn.commit()

    def send_simple_request_get(self, server_ip, server_port):

        """Send an HTTP GET."""

        url = f"http://{str(server_ip)}:{server_port}/simple"
        request_send_time = str(datetime.datetime.now())
        host_id = os.getlogin()
        ms_id = "/simple"
        res = requests.get(url).json()
        res["host_id"] = host_id
        res["request_send_time"] = request_send_time
        res["ms_id"] = ms_id
        return res

    def send_with_payload_request_get(self, 
                                      server_ip,
                                      server_port,
                                      payload_size):
        """ 
        Send an HTTP GET with the return payload_size as an URL paramenter.
        """

        url = f"http://{str(server_ip)}:{server_port}/with-payload/{str(payload_size)}"


        request_send_time = str(datetime.datetime.now())
        host_id = os.getlogin()
        ms_id = "/with-payload"
        res = requests.get(url).json()
        res["host_id"] = host_id
        res["request_send_time"] = request_send_time
        res["ms_id"] = ms_id
        return res

    def send_with_payload_request_post(self,
                                       server_ip,
                                       server_port,
                                       payload_size):

        """Build an QoSRequestWithPayload and send an HTTP POST with it as
        the body.
        """

        url = f"http://{str(server_ip)}:{server_port}/with-payload"
        req_body = QoSRequestWithPayload("/with-payload", payload_size)
        req_body.send()
        res = requests.post(url, json=req_body.__dict__).json()
        request_send_time = req_body.request_send_time
        host_id = os.getlogin()

        ms_id = "/with-payload"
        res["host_id"] = host_id
        res["request_send_time"] = request_send_time
        res["request_payload_size"] = req_body.request_payload_size
        res["ms_id"] = ms_id
        return res

    def build_qos_trip(self, response_dict):

        """Build an QoSTrip object"""

        ms_id = response_dict["ms_id"]
        host_id = response_dict["host_id"]
        server_id = response_dict["server_id"]
        request_send_time = response_dict["request_send_time"]
        if ("request_payload_size" in response_dict):
            request_payload_size = response_dict["request_payload_size"]
        else:
            request_payload_size = 0
        request_receival_time = response_dict["request_receival_time"]
        response_send_time = response_dict["response_send_time"]
        if ("response_payload_size" in response_dict):
            response_payload_size = response_dict["response_payload_size"]
        else:
            response_payload_size = 0
        ms_trip = QoSTrip(ms_id,
                          host_id,
                          server_id,
                          request_send_time,
                          request_payload_size,
                          request_receival_time,
                          response_send_time,
                          response_payload_size)
        return ms_trip

    def insert_ms_trip(self, ms_trip):

        """Insert a ms_trip into the database"""

        self.cursor.execute((
            "INSERT INTO microservice_trip VALUES ("
            f"\"{ms_trip.host_id}\","
            f"\"{ms_trip.server_id}\","
            f"\"{ms_trip.ms_id}\","
            f"\"{self.exp_id}\","
            f"\"{ms_trip.request_send_time}\","
            f"\"{ms_trip.request_arrival_time}\","
            f"\"{ms_trip.request_payload_size}\","
            f"\"{ms_trip.response_send_time}\","
            f"\"{ms_trip.response_arrival_time}\","
            f"\"{ms_trip.response_payload_size}\")"))

    def execute_experiment(self, 
                           server_ip,
                           server_port,
                           method,
                           payload_size,
                           n_requests):

        """Make self.n_requests requests of type self.method"""

        if (method == "POST"):
            for i in range(n_requests):
                ms_trip = self.send_with_payload_request_post(server_ip,
                                                              server_port,
                                                              payload_size)
                ms_trip = self.build_qos_trip(ms_trip)
                self.insert_ms_trip(ms_trip)
            self.conn.commit()
        elif (method == "GET" 
              and (payload_size == None or payload_size == 0)):
            for i in range(n_requests):
                ms_trip = self.send_with_payload_request_get(server_ip,
                                                              server_port,
                                                              payload_size)
                ms_trip = self.build_qos_trip(ms_trip)
                self.insert_ms_trip(ms_trip)
            self.conn.commit()
        elif (method == "GET"):
            for i in range(n_requests):
                ms_trip = self.send_simple_request_get(server_ip,
                                                       server_port)
                ms_trip = self.build_qos_trip(ms_trip)
                self.insert_ms_trip(ms_trip)
            self.conn.commit()

    def show_results(self):

        """ Show the latency experienced during the experiment"""

        str_format = "%Y-%m-%d %H:%M:%S.%f"
        print(self.exp_id)
        results = self.cursor.execute((
            f"SELECT request_send_time, request_arrival_time, response_send_time, response_arrival_time FROM microservice_trip WHERE experiment_id = '{self.exp_id}'")).fetchall()
        print("╔═══════════════╦═════════════════╦══════════════════╗")
        print("║      RTT      ║  Uplink Latency ║ Downlink Latency ║")
        print("╠═══════════════╬═════════════════╬══════════════════╣")
        registry = [[], [], [], []]
        for result in results:
            req_send_time = datetime.datetime.strptime(result[0], 
                                                       str_format)
                                                       
            req_arrival_time = datetime.datetime.strptime(result[1],
                                                          str_format)
            res_send_time = datetime.datetime.strptime(result[2], 
                                                       str_format)
            res_arrival_time = datetime.datetime.strptime(result[3],
                                                          str_format)
            rtt = res_arrival_time - req_send_time
            rtt /= datetime.timedelta(seconds=1)
            registry[0].append(rtt)
            rtt = str(round(rtt, 6)).center(15)
            uplink_delay = req_arrival_time - req_send_time
            uplink_delay /= datetime.timedelta(seconds=1)
            registry[1].append(uplink_delay)
            uplink_delay = str(round(uplink_delay, 6)).center(17)
            downlink_delay = res_arrival_time - res_send_time
            downlink_delay /= datetime.timedelta(seconds=1)
            registry[2].append(downlink_delay)
            downlink_delay = str(round(downlink_delay, 6)).center(18)
            print(f"║{rtt}║{uplink_delay}║{downlink_delay}║")
        
        print("╠═══════════════╬═════════════════╬══════════════════╣")
        print("╠═══════════════╬═════════════════╬══════════════════╣")
        rtt = statistics.mean(registry[0])
        rtt = str(round(rtt, 6)).center(15)
        uplink_delay = statistics.mean(registry[1])
        uplink_delay = str(round(uplink_delay, 6)).center(17)
        downlink_delay = statistics.mean(registry[2])
        downlink_delay = str(round(downlink_delay, 6)).center(18)
        print(f"║{rtt}║{uplink_delay}║{downlink_delay}║")
        print("╚════════════════════════════════════════════════════╝")

