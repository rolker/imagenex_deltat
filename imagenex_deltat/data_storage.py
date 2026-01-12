#!/usr/bin/env python3

import sys

from struct import unpack

from .data_storage_837 import Ping837
from .data_storage_83p import Ping83P


def read_file(file_path):
    with open(file_path, 'rb') as infile:
        data = infile.read()
        data_length = len(data)
        i = 0
        while i < data_length:
            ping = None
            marker = data[i:i+3]
            if marker == b'83P':
                ping = Ping83P(data, i)
                i += ping.data_length
            elif marker == b'837':
                ping = Ping837(data, i)
                i += ping.data_length
            else:
                raise ValueError(f'Unknown marker {marker} at position {i}')
            yield ping
