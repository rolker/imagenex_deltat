#!/usr/bin/env python3

import socket
import struct
import sys

from imagenex_deltat import imagenex




class NetworkListener:
  def __init__(self) -> None:
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    self.s.settimeout(0.1)
    self.s.bind(('', 4040))

  def run(self):
    while True:
      try:
        data, addr = self.s.recvfrom(2048)
        #print (data)
        format = '>3sBH2x11sx8sx3sx13sx13sxBHHHHHHHHBH'
        format_size = struct.calcsize(format)
        if len(data) >= format_size:
          parts = struct.unpack(format, data[:format_size])
          print(parts)
        p = imagenex.Ping(data)
      except socket.timeout:
        pass
  

class FileReader:
  def __init__(self):
    pass

  def read(self, filename):
    f = open(filename, 'rb')
    f.seek(0, 2)
    filesize = f.tell()
    f.seek(0,0)
    print(filename,filesize,'bytes')
    while True:
      header = f.read(6)
      if len(header) != 6:
        break
      f.seek(-6,1)
      marker, version, packet_size = struct.unpack('>3sBH', header[:6])
      print (marker, version, packet_size)
      data = f.read(packet_size)
      #p = imagenex.Ping(data)


if len(sys.argv) > 1:
  f = FileReader()
  for arg in sys.argv[1:]:
    f.read(arg)
else:
  n = NetworkListener()
  n.run()
