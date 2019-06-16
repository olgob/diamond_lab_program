# -*- coding: utf-8 -*-

"""
This file contains the Qudi Hardware module dummyAcquisitionCard class.
Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.
Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

from core.module import Base
from interface.empty_interface import EmptyInterface


class AcquisitionCardDummy(Base, EmptyInterface):
    """ """

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.clock_channel = 0  # physical channel of the clock of the acquisition card
        self.clock_frequency = 100  # Data acquisition card clock frequency [Hz]
        self.analog_output_channel = 1  # physical channel of the scanner
        self.clock_running = False
        self.analog_signal_running = False
        self.total_out_channels = 1  # total number of channels on the acquisition card
        self.output_signal = 0

    def on_activate(self):
        """ Starts up the and configure the acquisition card at activation """
        pass

    def on_deactivate(self):
        """ Shut down  the acquisition card at activation """
        pass

    def set_clock_channel(self, clock_channel):
        """ Set the channel of the clock """
        self.clock_channel = clock_channel

    def get_clock_channel(self):
        """ Get the channel of the clock """
        return self.clock_channel

    def set_clock_frequency(self, clock_frequency):
        """ Set the frequency of the clock """
        if clock_frequency > 0:
            self.clock_frequency = clock_frequency
        else:
            self.log.error('Clock frequency must be positive. clock frequency is set to default value : 100 Hz')
        return

    def get_clock_frequency(self):
        """ Get the frequency of the clock """
        return self.clock_frequency

    def set_analog_output_channel(self, analog_output_channel):
        """ Set the channel of the analog output signal """
        if analog_output_channel > self.total_out_channels:
            self.log.error('Analog output channel out of bound. Chose a channel between 0 and {:d}'.format(
                self.total_out_channels))
        elif analog_output_channel == self.get_clock_channel():
            self.log.error('Clock is already running on this channel. Choose another one')
        else:
            self.analog_output_channel = analog_output_channel
        return

    def get_analog_output_channel(self):
        """ Get the channel of the analog output signal """
        return self.analog_output_channel

    def set_output_signal(self, output_signal):
        """ Set the output signal sent by the acquisition device on a channel """
        self.output_signal = output_signal
        return

    def get_output_signal(self):
        """ Get the output signal sent by the acquisition device on a channel """
        return self.output_signal

    def set_up_clock(self, clock_frequency=None, clock_channel=None):
        """ Configures the hardware clock of the acquisition card card to give the timing. """
        if self.clock_running:
            self.log.error('Another clock is already running, close this one first.')
        else:
            # configure the clock parameters and start the clock
            clock_frequency = self.get_clock_frequency()
            clock_channel = self.get_clock_channel()
            # start the clock on your device
            self.start_clock(clock_channel, clock_frequency)
        return

    def start_clock(self, clock_channel, clock_frequency):
        """ Start the hardware clock of the acquisition device """
        self.clock_running = True
        return

    def stop_clock(self):
        """ Stop the hardware clock of the acquisition device """
        self.clock_running = False
        return

    def close_clock(self):
        """ Close the hardware clock of the acquisition device """
        if self.analog_signal_running:
            self.log.error('Analog signal is sent using the clock of the device. Close the analog signal first.')
        else:
            # stop the clock of the device
            self.stop_clock()
        return

    def set_up_analog_output(self):
        """ Starts or restarts the analog output. """
        signal = self.get_output_signal()
        # send the signal to the output channel
        self.start_analog_output(self.analog_output_channel, signal)
        return

    def start_analog_output(self):
        """ Start to send the signal on the desired output channel"""
        if not self.clock_running:
            self.log.error('No clock is running. Start clock first.')
        if self.analog_signal_running:
            self.log.error('Analog signal is already running. Stop the analog signal first.')
        else:
            self.analog_signal_running = True
        return

    def stop_analog_output(self):
        """ Stop the analog output """
        if self.analog_signal_running:
            self.analog_signal_running = False
        else:
            self.log.error('No analog signal running.')
        return
