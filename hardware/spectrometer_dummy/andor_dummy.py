# -*- coding: utf-8 -*-
"""
This file contains the Qudi hardware dummy for andor camera devices.

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
import time

from core.module import Base
from interface.empty_interface import EmptyInterface


class AndorDummy(Base, EmptyInterface):
    """ This is the class to define the controls for the simple andor camera hardware """

    _modclass = 'SpectrometerAndorDummy'
    _modtype = 'hardware'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temperature = 25  # celsius degree unit
        self.cycle_time = 0.02  # second
        self.exposure_time = 0.02  # second
        self.number_accumulations = 1
        self.camera_width = 1024  # pixels
        self.camera_height = 768  # pixels
        self.spectrum = np.zeros(self.camera_width)

    def on_activate(self):
        """ Initialisation performed during activation of the module """
        self.log.warning('spectrometer_andor_dummy>activation')

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module """
        self.log.warning('spectrometer_andor_dummy>desactivation')

    def set_temperature(self, temperature):
        """ Set camera temperature """
        if -75 <= temperature <= 25:
            self.temperature = temperature
        else:
            self.log.warning('temperature must be between -75 and 25 Celsius degree')
        return

    def get_temperature(self):
        """ Get camera temperature """
        return self.temperature

    def set_cycle_time(self, cycle_time):
        """ Set camera cycle time (time between the start of two following acquisitions) """
        if 0 < cycle_time and cycle_time >= self.get_exposure_time():
            self.cycle_time = cycle_time
        elif cycle_time < self.get_exposure_time():
            self.log.warning('cycle time must be superior or equal to exposure time')
        else:
            self.log.warning('cycle time must be superior to 0')
        return

    def get_cycle_time(self):
        """ Get camera cycle time (time between the start of two following acquisitions) """
        return self.cycle_time

    def set_exposure_time(self, exposure_time):
        """ Set camera exposure time """
        if self.get_cycle_time() < exposure_time:
            self.log.warning('cycle time must be superior or equal to exposure time')
        else:
            self.exposure_time = exposure_time
        return

    def get_exposure_time(self):
        """ Get camera exposure time """
        return self.exposure_time

    def set_number_accumulations(self, number_accumulations):
        """ Set the camera number of accumulations """
        self.number_accumulations = number_accumulations

    def get_number_accumulations(self):
        """ Get the camera number of accumulations """
        return self.number_accumulations

    def get_camera_size(self):
        return self.camera_width, self.camera_height

    def get_sepctrum_data(self):
        return self.spectrum

    def take_spectrum(self):
        """ Acquire spectrum in counts / second"""
        # reset the spectrum
        self.spectrum = np.zeros(self.camera_width)
        # if no accumulation
        if self.get_number_accumulations() == 1:
            # simulate the time delay between each acquisition
            time.sleep(self.get_cycle_time() - self.get_exposure_time())
            # acquire spectrum
            self.spectrum = np.random.rand(self.get_camera_size()[0])*1000 / self.get_exposure_time()
        # if accumulation
        else:
            n = 0
            while n < self.get_number_accumulations():
                # simulate the time delay between each acquisition
                time.sleep(self.get_cycle_time() - self.get_exposure_time())
                # acquire spectrum and sum it to the previous ones
                self.spectrum += np.random.rand(self.get_camera_size()[0])*1000 / self.get_exposure_time()
                n += 1
            # average the spectrum
            self.spectrum /= n
        return self.spectrum

    def cooler_on(self):
        """ Activate the cooler on the camera """
        self.log.warning('camera cooler on')

    def cooler_off(self):
        """ Desactivate the cooler on the camera """
        self.log.warning('camera cooler off')
