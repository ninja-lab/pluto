# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 10:39:47 2021

@author: eriki
"""

from __future__ import print_function
from picosdk.discover import find_unit
from picosdk.device import ChannelConfig, TimebaseOptions
import matplotlib.pyplot as plt
#from ps6000 import PS6000_RANGE

with find_unit() as device:

    print("found PicoScope: %s" % (device.info,))

    channel_configs = [ChannelConfig('A', True)]#, 'DC', 10)]
    microsecond = 1.e-6
    # the entry-level scopes only have about 8k-samples of memory onboard for block mode, so only ask for 6k samples.
    timebase_options = TimebaseOptions(microsecond, None, 6000 * microsecond)

    times, voltages, overflow_warnings = device.capture_block(timebase_options, channel_configs)

    for channel, data in voltages.items():
        label = "Channel %s" % channel
        if channel in overflow_warnings:
            label += " (over range)"
        plt.plot(times, data, label=label)

    plt.xlabel('Time / s')
    plt.ylabel('Amplitude / V')
    plt.legend()
    plt.show()