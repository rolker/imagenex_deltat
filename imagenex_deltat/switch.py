import struct

class SwitchData:
    """
    Used to communicate with the Model 837 DeltaT Sonar Head.
    From the docs: "To interrogate the head and receive echo data,
      a command program sends a Switch Data Command string to the
      sonar head. When the Switch Data command is accepted, the
      sonar head transmits, receives and sends one packet of echo
      data back to the command program. The command program must
      interrogate the sonar head multiple times in order
      to receive all packets of echo data before the data can be
      processed."
    """

    switch_data_header_1 = 0xFE # byte 0, 254 decimal
    switch_data_header_2 = 0x44 # byte 1, 68 decimal
    head_id = 0x10 # byte 2


    # Maps valid range requests in meters to value to use in the
    # Switch Data packet. byte 3 
    range_table = {
        5:5,
        10:10,
        20:20,
        30:30,
        40:40,
        50:50,
        60:60,
        80:80,
        100:100,
        150:150,
        200:200,
        250:201,
        300:202
    }


    # byte 10, absorption in hundreds of dB/m, range 0 to 2.55dB/m
    default_absorptions = {
        120000: 3,
        260000: 10,
        675000: 20,
        1700000: 170
    }

    # byte 20, resolution in bits.
    data_bits = 8

    # byte 22, run mode bits
    transmit_disabled_bit = 0b00000001
    tvg_disabled_bit =      0b00000010
    auto_gain_bit =         0b00010000

    # byte 25, frequency in hz to byte code
    frequency_table = {
        120000: 58,
        260000: 86,
        675000: 169,
        1700000: 68
    }

    # byte 26, termination byte (253 decimal)
    termination_byte = 0xFD

    def __init__(self):
        
        
        # used in bytes 5-6 when using automatic gain control
        # should consist of physical mounting offset and/or roll angle
        self._nadir_offset_angle = 0
        
        # 0 to 20dB in 1dB increments
        self._start_gain = 0

        # "When using Automatic Gain Control (Byte 22, Bit 4), this number
        # is used as a set point for adjusting the internal hardware gain
        # For strong bottom returns, use a low threshold value. For weak
        # bottom returns, use a high threshold value. A value of 120 is a
        # typical threshold value for a sandy bottom."
        self._agc_threshold = 120

        # Optional pusle length to use in microseconds if not using the 
        # recommended default for a given range. 10 to 1000 usec in 10 usec
        # increments. byte 14 = pulse length in usec / 10
        self._pulse_length_override = None

        # Number of data points to return in thousounds. 8 or 16 for 8000
        # or 16000
        self._data_points = 16

        # byte 21, commands for the optional internal pitch/roll/heading 
        # sensor
        # 0x00 – No PRH sensor installed (no PRH sensor interrogation)
        # 0x02 – Start compass calibration
        # 0x03 – Stop compass calibration
        # 0x04 – Start Pitch / Roll calibration
        # 0x05 – Stop Pitch / Roll calibration
        # 0x80 – Output gyro stabilized Euler angles
        self._prh_command = 0x00

        # byte 22, run mode
        # Bit 0 – Xmit Disable, set to 1 to disable the transmitter
        # Bit 1 – TVG Disable, set to 1 to disable Time Varied Gain
        #  amplification
        # Bit 2 – Reserved for Internal Use
        # Bit 3 – Reserved for Internal Use
        # Bit 4 – Auto Gain, set to 1 to enable Automatic Gain Control.
        #  If the sonar head transducer is pointing at an angle other
        #  than straight down, the mounting angle and/or the roll angle
        #  must be loaded into Nadir Offset Angle (see description for
        #  Bytes 5-6). An AGC Threshold value must also be loaded into
        #  Byte 11.
        # Bit 5 – Reserved for Internal Use
        # Bit 6 – Reserved for Internal Use
        # Bit 7 – Reserved for Internal Use
        self._transmit_disabled = False
        self._tvg_disabled = False
        self._auto_gain_enabled = False

        # byte 24, switch delay, 0 to 500ms
        # encoded as delay in ms/2 
        self._switch_delay = 0

        # byte 25
        self._frequency = SwitchData.frequency_table[260000]

        

