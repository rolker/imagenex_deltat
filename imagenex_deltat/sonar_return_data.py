from struct import unpack
from . import utils

class SonarReturnDataHeaderCommon:
    data_length = 12


    def __init__(self, data, i=0):
        if len(data) >= i+self.data_length: 
            values = unpack('>3sBBBBB2xH', data[i:i+12])

            self.data_format = values[0]
            self.head_id = values[1]

            serial_status = values[2]
            self.switch_setting_error = bool(serial_status&0x01)
            self.internal_prh_sensor_timeout = bool(serial_status&0x04)
            self.switch_accepted = bool(serial_status&0x40)
            self.character_overrun = bool(serial_status&0x80)

            self.packet_number = values[3]
            self.firmware_version = values[4]&0x0F
            self.range = utils.code_to_range[values[5]]
            self.data_bytes = values[6]


    def __repr__(self):
        return f"""Data format: {self.data_format} head id: {self.head_id}
  Switch setting error: {self.switch_setting_error}
  Internal PRH sensor timeout: {self.internal_prh_sensor_timeout}
  Switch accepted: {self.switch_accepted}
  Character overrun: {self.character_overrun}
  Packet number: {self.packet_number}
  Firmware version: {self.firmware_version}
  Range: {self.range}
  Data bytes: {self.data_bytes}"""


class SonarReturnData(SonarReturnDataHeaderCommon):
    data_length = 1033

    prh_sensor_status_table = {
        0:'no sensor installed',
        1:'PRH sensor installed (837A)',
        2:'PRH sensor installed (837B, signs reveresed)',
        5:'PRH sensor installed (837)'
    }

    def __init__(self, data, i=0):
        super().__init__(data, i)
        print('data len:',len(data))
        start_i = i
        i += super().data_length
        trigger_status = unpack('>B', data[i:i+1])[0]
        self.external_trigger_supported = bool(trigger_status&0x01)
        self.external_trigger_configured_as_output = bool(trigger_status&0x02)
        self.transmit_occured_after_trigger = bool(trigger_status&0x80)
        i += 1

        prh_status = unpack('>B', data[i:i+1])[0]
        if prh_status in self.prh_sensor_status_table.keys():
            self.attitude_sensor_status = self.prh_sensor_status_table[prh_status]
        else:
            self.attitude_sensor_status = None
        i += 1

        pitch, roll, heading = unpack('>3h', data[i:i+6])
        i += 6
        self.pitch = pitch * 360/65536
        self.roll = roll * 360/65536
        self.heading = heading * 360/65536

        self.timer_ticks = unpack('>h', data[i: i+2])[0]
        i += 2

        self.run_mode = unpack('>B', data[i: i+1])[0]
        i += 1

        self.gain = unpack('>xB', data[i:i+2])[0]
        i += 2

        self.agc_range_bin, self.agc_maximum_value = unpack('>2H', data[i: i+4])
        i += 4

        i += 3 # reserved

        print(i, i-start_i)

        self.echo_data = data[i: i+1000]
        i += 1000

        print(i, i-start_i)

        termination_byte = unpack('>B', data[i:i+1])[0]
        if termination_byte != 0xFC:
            raise ValueError(
                f'expected terminiation byte 0xFC but got 0x {termination_byte:02x}'
            )



        

    def __repr__(self):
        return f'''{super().__repr__()}
  trigger supported: {self.external_trigger_supported}, as output: {self.external_trigger_configured_as_output}, trigger found: {self.transmit_occured_after_trigger}
  attitude sensor status: {self.attitude_sensor_status}
  pitch: {self.pitch}, roll: {self.roll}, heading: {self.heading}
  timer ticks: {self.timer_ticks}, run mode: {self.run_mode}
  gain: {self.gain}, agc range bin: {self.agc_range_bin}, agc max: {self.agc_maximum_value}
  
'''