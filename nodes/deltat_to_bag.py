#!/usr/bin/env python3

import sys

from imagenex_deltat.data_storage import Ping837

with open(sys.argv[1], 'rb') as infile:
    data = infile.read()
    i = 0
    while i < len(data):
        p = Ping837(data)
        print(p)
        i += p.data_length
