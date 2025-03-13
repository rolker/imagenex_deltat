#!/usr/bin/env python3

import socket

from .sonar_return_data import SonarReturnData
from .switch import SwitchData

class DeltaT:
    def __init__(self, ip_address='192.168.0.2', port=4040):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_address,port))

        self.switch = SwitchData()

    def ping(self):
        ping_data = []
        for switch_packet in self.switch.get_ping_requests():
            self.socket.send(switch_packet)
            response = self.socket.recv(2000)
            ping_data.append(SonarReturnData(response))
        return ping_data

