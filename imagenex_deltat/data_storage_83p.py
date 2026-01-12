#!/usr/bin/env python3

from struct import unpack

class FileHeader83P:
    data_length = 256

    def __init__(self, data, i=0):
        if len(data) < i+FileHeader83P.data_length:
            raise IndexError(f'Trying to read {FileHeader83P.data_length} bytes at position {i} of {len(data)} bytes available. Only {len(data)-i} bytes remaining.')
        self.marker, self.version, self.total_bytes = unpack('>3sBH', data[i:i+6])

        self.date = unpack('>11s', data[i+8:i+19])[0]
        self.time = unpack('>8s', data[i+20:i+28])[0]
        self.deciseconds = unpack('>3s', data[i+29:i+32])[0]
        self.milliseconds = unpack('>4s', data[i+112:i+116])[0]

        self.lat_string, self.lon_string = unpack('>14s14s', data[i+33:i+61])

        self.speed = unpack('>B', data[i+61:i+62])[0]/10.0

        self.course = unpack('>H', data[i+62:i+64])[0]/10.0

        pitch, roll, heading = unpack('>3h', data[i+64:i+70])

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

        self.beam_count = unpack('>H', data[i+70:i+72])[0]
        self.samples_per_beam = unpack('>H', data[i+72:i+74])[0]
        self.sector_size = unpack('>H', data[i+74:i+76])[0]
        self.start_angle = unpack('>H', data[i+76:i+78])[0]/100.0
        self.angle_increment = unpack('>B', data[i+78:i+79])[0]/100.0

        self.range = unpack('>H', data[i+79:i+81])[0]
        self.frequency = unpack('>H', data[i+81:i+83])[0]*1000
        sound_speed = unpack('>H', data[i+83:i+85])[0]
        if sound_speed&0x8000:
            self.sound_speed = (sound_speed&0x7fff)/10.0
        else:
            self.sound_speed = 1500.0

        self.range_resolution = unpack('>H', data[i+85:i+87])[0]/1000.0

        self.profile_tilt_angle = unpack('>H', data[i+89:i+91])[0]-180.0
        self.repetition_rate = unpack('>H', data[i+91:i+93])[0]/1000.0

        self.ping_number = unpack('>I', data[i+93:i+97])[0]

        self.x_offset, self.y_offset, self.z_offset = unpack('>3f', data[i+100:i+112])

        intensity_bytes_included = unpack('>B', data[i+117:i+118])[0]
        self.has_intensity = intensity_bytes_included == 1

        self.ping_latency = unpack('>H', data[i+118:i+120])[0]/10000.0
        self.data_latency = unpack('>H', data[i+120:i+122])[0]/10000.0

        sample_rate = unpack('>B', data[i+122:i+123])[0]
        self.high_resolution = sample_rate == 1
        options_flags = unpack('>B', data[i+123:i+124])[0]
        self.roll_corrected = options_flags & 0x01 > 0
        self.ray_bending_corrected = options_flags & 0x02 > 0
        self.overlapped_mode = options_flags & 0x04 > 0

        self.number_of_pings_averaged = unpack('>B', data[i+125:i+126])[0]

        self.center_ping_time_offset = unpack('>H', data[i+126:i+128])[0]/10000.0

        self.external_heave = unpack('<f', data[i+128:i+132])[0]
        self.user_defined_byte = unpack('>B', data[i+132:i+133])[0]

        self.altitude = unpack('<f', data[i+133:i+137])[0]

        external_sensor_flags = unpack('>B', data[i+137:i+138])[0]

        self.external_heading_available = external_sensor_flags & 0x01 > 0
        self.external_roll_available = external_sensor_flags & 0x02 > 0
        self.external_pitch_available = external_sensor_flags & 0x04 > 0
        self.external_heave_available = external_sensor_flags & 0x08 > 0

        self.external_pitch = unpack('<f', data[i+138:i+142])[0]
        self.external_roll = unpack('<f', data[i+142:i+146])[0]
        self.external_heading = unpack('<f', data[i+146:i+150])[0]

        transmit_scan_flag = unpack('>B', data[i+150:i+151])[0]
        self.auto_scan = transmit_scan_flag == 1

        self.transmit_scan_angle = unpack('<f', data[i+151:i+155])[0]

        self.ranges = []

        for beam_number in range(self.beam_count):
            r = unpack('>H', data[i+256+beam_number*2:i+258+beam_number*2])[0]
            r *= self.range_resolution
            r *= self.sound_speed/1500.0
            self.ranges.append(r)



    def __repr__(self):
        return f'''
marker: {self.marker}, version: {self.version}, total bytes: {self.total_bytes}
date: {self.date}, time: {self.time}, deciseconds: {self.deciseconds}, milliseconds: {self.milliseconds}
latitude: {self.lat_string}, longitude: {self.lon_string}
speed: {self.speed}, course: {self.course}
pitch: {self.pitch}, roll: {self.roll}, heading: {self.heading}
beam count: {self.beam_count}, samples per beam: {self.samples_per_beam}, sector size: {self.sector_size}, start angle: {self.start_angle}, angle increment: {self.angle_increment}
range: {self.range}, frequency: {self.frequency}, sound speed: {self.sound_speed}, range resolution: {self.range_resolution}
profile tilt angle: {self.profile_tilt_angle}, repetition rate: {self.repetition_rate}, ping number: {self.ping_number}
x offset: {self.x_offset}, y offset: {self.y_offset}, z offset: {self.z_offset}, has intensity: {self.has_intensity}
ping latency: {self.ping_latency}, data latency: {self.data_latency}, high resolution: {self.high_resolution}, roll corrected: {self.roll_corrected}, ray bending corrected: {self.ray_bending_corrected}, overlapped mode: {self.overlapped_mode},
number of pings averaged: {self.number_of_pings_averaged}, center ping time offset: {self.center_ping_time_offset}, altitude: {self.altitude}
external heading available: {self.external_heading_available}, external roll available: {self.external_roll_available}, external pitch available: {self.external_pitch_available}, external heave available: {self.external_heave_available}
external heading: {self.external_heading}, external roll: {self.external_roll}, external pitch: {self.external_pitch}, external heave: {self.external_heave}
auto scan: {self.auto_scan}, transmit scan angle: {self.transmit_scan_angle}
'''

class Ping83P(FileHeader83P):
    def __init__(self, data, i=0):
        super().__init__(data, i)


    @property
    def data_length(self):
        return self.total_bytes

    def __repr__(self):
        return f'''{super().__repr__()}'''
    