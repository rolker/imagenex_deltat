#!/usr/bin/env python3

import socket

dt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dt.bind(('', 4040))
while True:
    data, addr = dt.recvfrom(1024)
    print(data[:3])
    print(addr)
    