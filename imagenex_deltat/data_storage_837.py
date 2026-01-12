#!/usr/bin/env python3

from struct import unpack
from .sonar_return_data import SonarReturnDataHeaderCommon

class FileHeader837:
    data_length = 100 # File header size

    def __init__(self, data, i=0):
        if len(data) < i+FileHeader837.data_length:
            raise IndexError(f'Trying to read {FileHeader837.data_length} bytes at position {i} of {len(data)} bytes available. Only {len(data)-i} bytes remaining.') 
        self.marker, number_to_read_index, self.total_bytes = unpack('>3sBH', data[i:i+6])

        self.number_of_data_bytes = {10:8000, 11:16000}[number_to_read_index]

        self.num_of_bytes_from_sonar = unpack('>H', data[i+6:i+8])[0]

        self.date = unpack('>11s', data[i+8:i+19])[0]
        self.time = unpack('>8s', data[i+20:i+28])[0]
        self.deciseconds = unpack('>3s', data[i+29:i+32])[0]
        self.milliseconds = unpack('>4s', data[i+93:i+97])[0]

        self.video_frame_length = unpack('>4B', data[i+33:i+37])[0]
        if self.video_frame_length&0x80000000:
            self.video_frame_length &= 0x7FFFFFFF
        else:
            self.video_frame_length = 0
        self.display_mode = unpack('>B', data[i+37:i+38])[0]
        self.transducer_up = not self.display_mode & 0b01000000 == 0
        self.display_mode = self.display_mode & 0b0111

        self.start_gain = unpack('>B', data[i+38:i+39])[0]

        tilt_bytes = unpack('>2B', data[i+39:i+41])
        if tilt_bytes[0] & 0b10000000:
            self.tilt_angle = ((tilt_bytes[0]&0x7F)<<8|(tilt_bytes[1]))/10.0-180.0
        else:
            self.tilt_angle = 0.0

        self.num_of_pings_averaged = unpack('>B', data[i+43:i+44])[0]

        self.pulse_length = (unpack('>B', data[i+44:i+45])[0])*10

        sound_speed_bytes = unpack('>2B', data[i+46:i+48])
        if sound_speed_bytes[0]&0b10000000:
            self.sound_speed = 1500.0
        else:
            self.sound_speed = ((sound_speed_bytes[0]&0x7F)<<8|(sound_speed_bytes[1]))/10.0

        self.lat_string, self.lon_string = unpack('>14s14s', data[i+48:i+76])

        self.speed = unpack('>B', data[i+76:i+77])[0]/10.0

        self.course = unpack('>H', data[i+77:i+79])[0]/10.0

        self.frequency = unpack('>H', data[i+80:i+82])[0]*1000

        pitch, roll, heading = unpack('>3h', data[i+82:i+88])

        if pitch&0x8000:
            self.pitch = ((pitch&0x7FFF)-900)/10.0
        else:
            self.pitch = None

        if roll&0x8000:
            self.roll = ((roll&0x7fff)-900)/10.0
        else:
            self.roll = None

        if heading&0x8000:
            self.heading = (heading&0x7fff)/10.0
        else:
            self.heading = None

        
        self.ping_period = unpack('>H', data[i+88:i+90])[0]


        self.display_gain = unpack('>B', data[i+90:i+91])[0]


    def __repr__(self):
        return f'''
marker: {self.marker}, sonar data bytes: {self.number_of_data_bytes} total bytes: {self.total_bytes}
  number of bytes from sonar: {self.num_of_bytes_from_sonar}
  {self.date} {self.time}{self.milliseconds}
  video frame length: {self.video_frame_length}
  start gain: {self.start_gain}, num of avg'd pings: {self.num_of_pings_averaged}
  pulse length: {self.pulse_length} us, sound speed: {self.sound_speed}
  {self.lat_string}, {self.lon_string}
  speed: {self.speed} knots, course: {self.course} degrees
  frequency: {self.frequency}
  pitch: {self.pitch}, roll: {self.roll}, heading: {self.heading}
  ping period: {self.ping_period} ms'''



class Ping837(FileHeader837):
    def __init__(self, data, i = 0):
        """
        Decode a ping from a .837 file containing raw data.
        """
        super().__init__(data, i)
        start_i = i
        i += super().data_length
        self.sonar_data_header = SonarReturnDataHeaderCommon(data, i)
        i += self.sonar_data_header.data_length
        data_size = self.number_of_data_bytes
        self.sonar_data = data[i:i+data_size]
        i += data_size
        termination_byte = data[i]
        if termination_byte != 0xFC:
            raise ValueError(
                f'expected terminiation byte 0xFC but got 0x {termination_byte:02x}'
            )
        i += 1
        self.sonar_offsets = unpack('>3f', data[i:i+12])
        i += 12
        self.sensor_type = unpack('>B', data[i:i+1])[0]
        i += 1
        self.prh = unpack('>3H', data[i:i+6])
        i += 6
        self.timer_ticks = unpack('>H', data[i:i+2])[0]
        i += 2
        self.azimuth_head_position = unpack('>H', data[i:i+2])[0]
        i += 2
        self.azimuth_up = unpack('>B', data[i:i+1])[0]
        i += 1
        self.heave = unpack('>f', data[i:i+4])[0]
        i += 4
        self.reserved = unpack('>7B', data[i:i+7])
        i += 7

        self.bytes_decoded = i - start_i

    @property
    def data_length(self):
        return self.total_bytes

    def __repr__(self):
        return f'''{super().__repr__()}
  {self.sonar_data_header}
  data: {unpack('>5B',self.sonar_data[:5])} ... {unpack('>5B',self.sonar_data[-5:])}
  sonar offsets: {self.sonar_offsets}, sensor type: {self.sensor_type}
  pitch, roll, heading: {self.prh}, heave: {self.heave}
  timer ticks: {self.timer_ticks}
  azimuth head pos: {self.azimuth_head_position}, azimuth up/down: {self.azimuth_up}
  bytes decoded: {self.bytes_decoded}
'''



