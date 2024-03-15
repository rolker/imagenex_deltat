#!/usr/bin/env python3

import socket
import struct
import math

class Ping:
  def __init__(self, data):
    data_size = len(data)
    if data_size > 6:
      self.marker, self.version, self.packet_size = struct.unpack('>3sBH', data[:6])
      print (self.packet_size)
      self.date = struct.unpack('>11s', data[8:19])[0]
      self.time = struct.unpack('>8s', data[20:28])[0]
      self.seconds = struct.unpack('>3s', data[29:32])[0]
      print (self.date, self.time, self.seconds)
      self.beam_count = struct.unpack('>H', data[70:72])[0]
      self.samples_per_beam = struct.unpack('>H', data[72:74])[0]
      self.sector_size = struct.unpack('>H', data[74:76])[0]
      self.start_angle = -180+(struct.unpack('>H', data[76:78])[0]/100.0)
      self.angle_increment = struct.unpack('>B', data[78:79])[0]/100.0
      self.range = struct.unpack('>H', data[79:81])[0]
      self.frequency = struct.unpack('>H', data[81:83])[0]
      self.sound_speed = struct.unpack('>H', data[83:85])[0]/10.0
      self.range_resolution = struct.unpack('>H', data[85:87])[0]/1000.0
      self.tilt_angle = struct.unpack('>H', data[89:91])[0]-180
      self.ping_period = struct.unpack('>H', data[91:93])[0]/1000.0
      print('beam count:', self.beam_count, 'samples:', self.samples_per_beam, 'sector size (deg):', self.sector_size, 'start angle:', self.start_angle, "angle inc:", self.angle_increment, 'range:', self.range, 'freq:', self.frequency, 'ss:', self.sound_speed, 'resolution:', self.range_resolution, 'tilt', self.tilt_angle, 'ping period:', self.ping_period)

      self.ping_number = struct.unpack('>I', data[93:97])[0]
      self.ping_ms = struct.unpack('>4s', data[112:116])
      self.ping_has_intensity = struct.unpack('>B', data[117:118])[0]
      self.ping_latency = struct.unpack('>H', data[118:120])[0]/10000.0
      self.data_latency = struct.unpack('>H', data[120:122])[0]/10000.0
      self.high_resolution = struct.unpack('>B', data[122:123])[0]
      self.options = struct.unpack('>B', data[123:124])[0]
      self.ping_average_count = struct.unpack('>B', data[125:126])[0]
      self.center_ping_time_offset = struct.unpack('>H', data[126:128])[0]/10000.0
      print('ping:', self.ping_number, "ms:", self.ping_ms, "intensity?", self.ping_has_intensity, 'ping latency:', self.ping_latency, 'data latency:', self.data_latency, 'hi res?', self.high_resolution, 'options:', self.options, 'no of avg pings', self.ping_average_count, 'ctr ping time off:', self.center_ping_time_offset)

      self.altitude = struct.unpack('<f', data[133:137])[0]
      self.auto_scan = struct.unpack('>B', data[150:151])[0]
      self.transmit_scan_angle = struct.unpack('<f', data[151:155])[0]
      print('altitude', self.altitude, 'auro scan?', self.auto_scan, 'transmit scan angle', self.transmit_scan_angle)

      self.ranges = struct.unpack('<'+str(self.beam_count)+'H', data[256:(256+2*self.beam_count)])
      self.range_meters = []
      for r in self.ranges:
        self.range_meters.append(r*self.range_resolution)
      print(self.range_meters)

      if self.ping_has_intensity:
        self.intensities = struct.unpack('<'+str(self.beam_count)+'H', data[256+(2*self.beam_count):256+(4*self.beam_count)])
        print(self.intensities)

      for i in range(self.beam_count):
        angle = self.start_angle+i*self.angle_increment
        radians = math.radians(angle)
        c = math.cos(radians)
        depth = c*self.range_meters[i]
        print(i, self.start_angle+i*self.angle_increment, depth)


      



s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.settimeout(0.1)
s.bind(('', 4040))

while True:
  try:
    data, addr = s.recvfrom(2048)
    #print (data)
    format = '>3sBH2x11sx8sx3sx13sx13sxBHHHHHHHHBH'
    format_size = struct.calcsize(format)
    if len(data) >= format_size:
      parts = struct.unpack(format, data[:format_size])
      print(parts)
    p = Ping(data)
  except socket.timeout:
    pass
  