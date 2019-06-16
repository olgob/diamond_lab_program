# -*- coding: utf-8 -*-
"""
This module operates an acquisition card.

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

import numpy as np
from logic.generic_logic import GenericLogic
from core.module import Connector


class AcquisitionCardLogic(GenericLogic):
    """
    This is the Logic class for controlling an acquisition card.
    """
    _modclass = 'AcquisitionCardLogic'
    _modtype = 'logic'

    # declare connectors
    acquisition_card = Connector(interface='EmptyInterface')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.clock_running = False
        self.analog_signal_running = False
        return

    def on_activate(self):
        """ Initialisation performed during activation of the module"""
        self._acquisition_card = self.acquisition_card()

    def create_ramp(self, t, amplitude, frequency, offset):
        """ Get a ramp function """
        ramp = np.zeros(len(t))
        period = 1.0 / frequency
        for i in range(len(t)):
            x = t[i] % period
            if x < period / 2:
                ramp[i] = amplitude * x / (period / 2) + offset - 0.5 * amplitude
            else:
                ramp[i] = 2 * amplitude - amplitude * x / (period / 2) + offset - 0.5 * amplitude
        return ramp

    def create_sine_wave(self, t, amplitude, offset, frequency):
        """ Generate a sine wave function """
        sinewave = amplitude * np.sin(2 * np.pi * frequency * t) + offset
        return sinewave

    def create_sine_wave_signal(self, amplitude, frequency, offset):
        """ Generates a sine wave signal to be send on the analog output of the acquisition card """
        # the number of samples is calculated to get the desired frequency of the sine wave on the output of the
        # acquisition card
        samples_number = self._acquisition_card.get_clock_frequency() / frequency
        if samples_number < 2 * frequency:
            self.log.error('The samples number does not respect the Nyquist criteria.'
                           'Raise the clock frequency to generate this signal. '
                           'Zeros signal is created instead')
            signal = np.zeros(self._acquisition_card.get_clock_frequency())
        else:
            # the time is fixed so that we have one full period of the sine wave
            t = np.linspace(0, 1 / frequency, samples_number)
            # the sine wave signal is calculated
            signal = self.create_sine_wave(t, amplitude, frequency, offset)
        return signal

    def create_ramp_signal(self, amplitude, frequency, offset):
        """ Generates a sine wave signal to be send on the analog output of the acquisition card """
        # the number of samples is calculated to get the desired frequency of the sine wave on the output of the
        # acquisition card
        samples_number = self._acquisition_card.get_clock_frequency() / frequency
        # the time is fixed so that we have one full period of the sine wave
        t = np.linspace(0, 1 / frequency, samples_number)
        # the sine wave signal is calculated
        signal = self.create_ramp(t, amplitude, frequency, offset)
        return signal

    def start_sine_wave(self, amplitude, frequency, offset):
        """ Start to send a sine wave signal to the analog output of the acquisition card """
        if not self.clock_running:
            self._acquisition_card.start_clock(self._acquisition_card.get_clock_channel(),
                                               self._acquisition_card.get_clock_frequency())
            self.clock_running = True
        if self.analog_signal_running:
            self._acquisition_card.stop_analog_output()
            self.analog_signal_running = False
        signal = self.create_sine_wave_signal(amplitude, frequency, offset)
        self._acquisition_card.set_output_signal(signal)
        self._acquisition_card.start_analog_output()
        self.analog_signal_running = True
        return

    def start_ramp(self, amplitude, frequency, offset):
        """ Start to send a sine wave signal to the analog output of the acquisition card """
        if not self.clock_running:
            self._acquisition_card.start_clock(self._acquisition_card.get_clock_channel(),
                                               self._acquisition_card.get_clock_frequency())
            self.clock_running = True
        if self.analog_signal_running:
            self._acquisition_card.stop_analog_output()
        signal = self.create_ramp_signal(amplitude, frequency, offset)
        self._acquisition_card.set_output_signal(signal)
        self._acquisition_card.start_analog_output()
        self.analog_signal_running = True
        return

    def start_offset(self, offset):
        """Send an offset signal on the scanner"""
        if not self.clock_running:
            self._acquisition_card.start_clock(self._acquisition_card.get_clock_channel(),
                                               self._acquisition_card.get_clock_frequency())
            self.clock_running = True
        if self.analog_signal_running:
            self._acquisition_card.stop_analog_output()
        signal = np.full(self._acquisition_card.get_clock_frequency(), offset)
        self._acquisition_card.set_output_signal(signal)
        self._acquisition_card.start_analog_output()
        self.analog_signal_running = True
        return

    def stop_analog_output(self):
        """ Stop to send a signal to the analog output of the acquisition card """
        self._acquisition_card.stop_analog_output()
        self._acquisition_card.close_clock()
        self.clock_running = False
        return
