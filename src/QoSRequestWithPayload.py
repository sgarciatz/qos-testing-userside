
import os
import datetime
import base64


class QoSRequestWithPayload(object):


    """
    The same as QoSRaquest but with a sizable payload
    """

    def __init__(self, ms_id: str, payload_size: int) -> None:

        """
        Constructs a QoSResponseWithPayload
        """
        
        self.host_id = os.getlogin()
        self.request_send_time = str(datetime.datetime.now())
        self.ms_id = ms_id
        self.request_payload = "0" * payload_size
        self.request_payload_size = len(self.request_payload)

    def send(self) -> None:

        """
        This method must be called before sending the response in order
        to establish the dispatch_time.
        """

        self.request_send_time = str(datetime.datetime.now())

    def to_json(self) -> dict:

        """
        Returns a serializable dict.
        """
        
        return self.__dict__
