#!/usr/bin/env python3

from struct import unpack


class FileHeader837:
    data_length = 100 # File header size

    def __init__(self, data):
        if len(data) >= self.data_length: 
            self.marker, self.number_to_read_index, self.total_bytes = unpack('>3sBH', data[:6])
            self.num_of_bytes_from_sonar = unpack('>H', data[6:8])[0]

            self.date, self.time, self.deciseconds = unpack('>11s8s3s', data[8:32])
            self.milliseconds = unpack('>4s', data[93:97])[0]

            self.video_frame_length = unpack('>4B', data[33:37])
            self.display_mode = unpack('>B', data[37:38])[0]
            self.transducer_up = not self.display_mode & 0b01000000 == 0
            self.display_mode = self.display_mode & 0b0111

            self.start_gain = unpack('>B', data[38:39])[0]

            tilt_bytes = unpack('>2B', data[39:41])
            if tilt_bytes[0] & 0b10000000:
                self.tilt_angle = ((tilt_bytes[0]&0x7F)<<8|(tilt_bytes[1]))/10.0-180.0
            else:
                self.tilt_angle = 0.0

            self.num_of_pings_averaged = unpack('>B', data[43:44])[0]

            self.pulse_length = (unpack('>B', data[44:45])[0])*10

            sound_speed_bytes = unpack('>2B', data[46:48])
            if sound_speed_bytes[0]&0b10000000:
               self.sound_speed = 15000.0
            else:
              self.sound_speed = ((sound_speed_bytes[0]&0x7F)<<8|(sound_speed_bytes[1]))/10.0

            self.lat_string, self.lon_string = unpack('>14s14s', data[48:76])

            self.speed = unpack('>B', data[76:77])[0]/10.0

            self.course = unpack('>H', data[77:79])/10.0

            frequency = unpack('>H', data[80:82])[0]*1000

            pitch, roll, heading = unpack('>3h', data[82:88])

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

            
            self.ping_period = unpack('>H', data[88:90])[0]


            self.display_gain = unpack('>B', data[90:91])[0]

            self.extra_bytes = data[self.data_length:]

    def __repr__(self):
        return f'''
        marker: {self.marker}, number to read index: {self.number_to_read_index} total bytes: {self.total_bytes}
        number of bytes from sonar: {self.num_of_bytes_from_sonar}
        {self.date} {self.time}{self.milliseconds}
        start gain: {self.start_gain}, num of avg'd pings: {self.num_of_pings_averaged}
        pulse length: {self.pulse_length} us, sound speed: {self.sound_speed}
        {self.lat_string}, {self.lon_string}
        speed: {self.speed} knots, course: {self.course} degrees
        frequency: {self.frequency}
        pitch: {self.pitch}, roll: {self.roll}, heading: {self.heading}
        ping period: {self.ping_period} ms, 
        '''



def decode837(data):
    """
    Decode a ping from a .837 file containing raw data.
    """
    header = FileHeader837(data)
    print(header)

# test code below, delete once done

import sys
with open(sys.argv[1], 'rb') as infile:
   data = infile.read(20000)
   decode837(data)
