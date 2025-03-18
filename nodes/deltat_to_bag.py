#!/usr/bin/env python3

import sys
from struct import pack
from struct import unpack
import math
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import signal

from imagenex_deltat.data_storage import Ping837


with open(sys.argv[1], 'rb') as infile:
    data = infile.read()
    i = 0

    element_spacing = 0.0033
    cutoff_frequency_ratio = 75.0/34.0
    
    last_ping = None
    count = 0

    while i < len(data):
        p = Ping837(data, i)
        #print(p)
        print(f'\n** {p.date.decode()} {(p.time+p.milliseconds).decode()} **')
        print('frequency: ', p.frequency, 'Hz')
        print('range: ', p.sonar_data_header.range, 'm')
        print('pulse length: ', p.pulse_length, 'us')
        print('initial gain: ', p.start_gain)
        i += p.data_length

        two_way_travel_time = 2*p.sonar_data_header.range/1500.0
        bin_time_span = two_way_travel_time/500.0
        sampling_frequency = 1.0/bin_time_span
        print('sampling frequency', sampling_frequency)

        # delta frequency ratio from Patent US 7,212,466 B2, section 18
        delta_frequency = sampling_frequency/2.4615
        print('delta frequency', delta_frequency)

        reference_frequency = p.frequency+ delta_frequency
        print('reference frequency', reference_frequency)


        if last_ping is not None:

            last_ping_data = np.frombuffer(last_ping.sonar_data, dtype=np.uint8).reshape(500, 16).transpose()/255.0

            #print(last_ping_data[:, :6])

            ping_data = np.frombuffer(p.sonar_data, dtype=np.uint8).reshape(500, 16).transpose()#/255.0
            print(ping_data[:, 0:6])
            count += 1
            if count > 10:
                break

            for e in range(16):
                for s in range(6):
                    for b in range(8):
                        if ping_data[e,s] & 1<<(7-b):
                            print('1', end='')
                        else:
                            print('0', end='')
                    print(' ', end='')
                print('')
            print('')

            ping_difference = ping_data - last_ping_data

            #print('ping difference', ping_difference.shape, ping_difference.dtype)
            #print(ping_difference[:,:6])


            #print('ping raw data', ping_data.shape, ping_data.dtype)

            ping_frequency = np.fft.rfft(ping_data)
            #print('ping frequency', ping_frequency.shape, ping_frequency.dtype)

            #ping_frequency[:, 1:] *=2

            ping_complex = np.fft.ifft(ping_frequency, 500)

            #print('ping complex',ping_complex.shape)
            #print(ping_complex[:,:3])


            plot_elements = np.arange(-8, 8).reshape(16,1)*2+ping_data
            #plot_elements = np.arange(-8, 8).reshape(16,1)*2+ping_difference

            field_of_view = 2*math.asin(p.sound_speed/(2*p.frequency*element_spacing))
            #print('field of view', math.degrees(field_of_view))

            beam_angles = np.linspace(-field_of_view/2, field_of_view/2, 150).reshape(150, 1)


            radians_per_sample = 2*math.pi*p.frequency/sampling_frequency
            #print('radians per sample', radians_per_sample)

            elements = np.arange(-8, 8)
            #print('elements', elements)

            time_delays = elements*element_spacing*np.sin(beam_angles)/p.sound_speed
            #print('time delays', time_delays.shape, time_delays.dtype)
            #print('time delays first beam', time_delays[0])

            range_delays_in_samples = sampling_frequency*time_delays
            #print('range delays in samples', range_delays_in_samples.shape, range_delays_in_samples.dtype)
            #print('range delays in samples first beam', range_delays_in_samples[0])

            range_delays_in_radians = range_delays_in_samples*radians_per_sample
            #print('range delays in radians', range_delays_in_radians.shape, range_delays_in_radians.dtype)

            sample_numbers = np.arange(0, 500).reshape(1,1,500)+range_delays_in_samples.reshape(150,16,1)

            #print('sample numbers', sample_numbers.shape, sample_numbers.dtype)


            phases = sample_numbers*radians_per_sample

            phases_complex = np.exp(1j*phases)

            #print('phases complex', phases_complex.shape, phases_complex.dtype)


            phase_shifted_ping = ping_complex.reshape(1,16,500)*phases_complex

            ping_modified = np.sign(np.real(phase_shifted_ping))*np.sqrt(np.abs(np.real(phase_shifted_ping)))+ (np.sign(np.imag(phase_shifted_ping))*np.sqrt(np.abs(np.imag(phase_shifted_ping))))*1j
            #print ('ping modified',ping_modified.shape)


            beamformed = np.zeros((150,500), dtype=complex)
            for j in range(16):
                for k in range(j+1,16):
                    beamformed += ping_modified[:,j,:]*ping_modified[:,k,:]
                


            #beat_wave = np.exp(1j*2*math.pi*delta_frequency*np.arange(500)/sampling_frequency)

            # for j in range(16):
            #     plt.plot(plot_elements[j,:])



        last_ping = p




