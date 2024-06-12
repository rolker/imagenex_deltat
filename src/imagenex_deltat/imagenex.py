#!/usr/bin/env python3

import struct
import datetime



class Ping:
  def __init__(self, data):
    data_size = len(data)
    if data_size > 6:
      self.marker, self.version, self.packet_size = struct.unpack('>3sBH', data[:6])
      #print (self.marker)
      if self.marker.decode() == '83P':
        #print (self.packet_size)
        self.date = struct.unpack('>11s', data[8:19])[0]
        self.time = struct.unpack('>8s', data[20:28])[0]
        self.deciseconds = struct.unpack('>3s', data[29:32])[0]
        #print (self.date, self.time, self.deciseconds)
        self.beam_count = struct.unpack('>H', data[70:72])[0]
        self.samples_per_beam = struct.unpack('>H', data[72:74])[0]
        self.sector_size = struct.unpack('>H', data[74:76])[0]
        self.start_angle = -180+(struct.unpack('>H', data[76:78])[0]/100.0)
        self.angle_increment = struct.unpack('>B', data[78:79])[0]/100.0
        self.range = struct.unpack('>H', data[79:81])[0]
        self.frequency = struct.unpack('>H', data[81:83])[0]
        self.sound_speed = (struct.unpack('>H', data[83:85])[0]&0x7fff)/10.0
        self.range_resolution = struct.unpack('>H', data[85:87])[0]/1000.0
        self.tilt_angle = struct.unpack('>H', data[89:91])[0]-180
        self.ping_period = struct.unpack('>H', data[91:93])[0]/1000.0
        #print('beam count:', self.beam_count, 'samples:', self.samples_per_beam, 'sector size (deg):', self.sector_size, 'start angle:', self.start_angle, "angle inc:", self.angle_increment, 'range:', self.range, 'freq:', self.frequency, 'ss:', self.sound_speed, 'resolution:', self.range_resolution, 'tilt', self.tilt_angle, 'ping period:', self.ping_period)

        self.ping_number = struct.unpack('>I', data[93:97])[0]
        self.ping_ms = struct.unpack('>4s', data[112:116])[0]
        self.ping_has_intensity = struct.unpack('>B', data[117:118])[0]
        self.ping_latency = struct.unpack('>H', data[118:120])[0]/10000.0
        self.data_latency = struct.unpack('>H', data[120:122])[0]/10000.0
        self.high_resolution = struct.unpack('>B', data[122:123])[0]
        self.options = struct.unpack('>B', data[123:124])[0]
        self.ping_average_count = struct.unpack('>B', data[125:126])[0]
        self.center_ping_time_offset = struct.unpack('>H', data[126:128])[0]/10000.0
        #print('ping:', self.ping_number, "ms:", self.ping_ms, "intensity?", self.ping_has_intensity, 'ping latency:', self.ping_latency, 'data latency:', self.data_latency, 'hi res?', self.high_resolution, 'options:', self.options, 'no of avg pings', self.ping_average_count, 'ctr ping time off:', self.center_ping_time_offset)

        self.altitude = struct.unpack('<f', data[133:137])[0]
        self.auto_scan = struct.unpack('>B', data[150:151])[0]
        self.transmit_scan_angle = struct.unpack('<f', data[151:155])[0]
        #print('altitude', self.altitude, 'auro scan?', self.auto_scan, 'transmit scan angle', self.transmit_scan_angle)

        self.ranges = struct.unpack('>'+str(self.beam_count)+'H', data[256:(256+2*self.beam_count)])
        #print(self.ranges)
        self.range_meters = []
        for r in self.ranges:
          self.range_meters.append(r*self.range_resolution)
        #print(self.range_meters)

        if self.ping_has_intensity:
          self.intensities = struct.unpack('>'+str(self.beam_count)+'H', data[256+(2*self.beam_count):256+(4*self.beam_count)])
          #print(self.intensities)
        else:
          self.intensities = None
      if self.marker.decode() == '83B':
        self.date = struct.unpack('>11s', data[8:19])[0]
        self.time = struct.unpack('>8s', data[20:28])[0]
        self.deciseconds = struct.unpack('>3s', data[29:32])[0]

        self.latitude = struct.unpack('>14s', data[33:47])[0]
        self.longitude = struct.unpack('>14s', data[47:61])[0]

        self.speed = struct.unpack('B', data[61:62])[0]


        self.gps_heading = struct.unpack('>H', data[62:64])[0]/10.0
        self.pitch = struct.unpack('>H', data[64:66])[0]
        if self.pitch != 0:
          self.pitch = ((self.pitch & 0x7fff)-900)/10.0

        self.roll = struct.unpack('>H', data[66:68])[0]
        if self.roll != 0:
          self.roll = ((self.roll & 0x7fff)-900)/10.0

        self.heading = struct.unpack('>H', data[68:70])[0]
        if self.heading != 0:
          self.heading = (self.heading & 0x7fff)/10.0

        print (self.latitude, self.longitude, self.speed, self.heading, self.pitch, self.roll)

        self.beam_count = struct.unpack('>H', data[70:72])[0]
        self.samples_per_beam = struct.unpack('>H', data[72:74])[0]
        self.sector_size = struct.unpack('>H', data[74:76])[0]
        self.start_angle = -180+(struct.unpack('>H', data[76:78])[0]/100.0)
        self.angle_increment = struct.unpack('>B', data[78:79])[0]/100.0
        self.range = struct.unpack('>H', data[79:81])[0]
        self.frequency = struct.unpack('>H', data[81:83])[0]
        self.sound_speed = (struct.unpack('>H', data[83:85])[0]&0x7fff)/10.0
        self.range_resolution = struct.unpack('>H', data[85:87])[0]/1000.0
        self.pulse_length = struct.unpack('>H', data[87:89])[0]/1000000.0
        self.tilt_angle = struct.unpack('>H', data[89:91])[0]-180
        self.ping_period = struct.unpack('>H', data[91:93])[0]/1000.0
        print('beam count:', self.beam_count, 'samples:', self.samples_per_beam, 'sector size (deg):', self.sector_size, 'start angle:', self.start_angle, "angle inc:", self.angle_increment, 'range:', self.range, 'freq:', self.frequency, 'ss:', self.sound_speed, 'resolution:', self.range_resolution, 'pulse length', self.pulse_length,'tilt', self.tilt_angle, 'ping period:', self.ping_period)
        self.ping_number = struct.unpack('>I', data[93:97])[0]
        print('ping number', self.ping_number)



  def timestamp(self):
    day = int(self.date[0:2])
    month = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}[self.date[3:6].decode()]
    year = int(self.date[7:11])
    hour = int(self.time[0:2])
    minute = int(self.time[3:5])
    seconds = int(self.time[6:8])

    ms = float(self.ping_ms)
    return datetime.datetime(year, month, day, hour, minute, seconds, int(ms*1000000), tzinfo=datetime.timezone.utc)
