# -*- coding: utf-8 -*-
"""
This file contains the Qudi hardware dummy for shamrock spectrometer.

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


class ShamrockDummy(Base, EmptyInterface):

    """This is the Interface class to define the controls of a spectrometer.
    """
    _modclass = 'ShamrockDummy'
    _modtype = 'hardware'

    # config

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.center_wavelength = 633  # nm
        self.grating = 0  # 0: 150 lines / mm, 1: 300 lines / mm, 2: 1200 lines / mm
        self.wavelength_min = self.center_wavelength - 357 / 2
        self.wavelength_max = self.center_wavelength + 357 / 2

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """
        self.log.warning('shamrock_dummy>activation')

    def on_deactivate(self):
        """ Desinitialisation performed during deactivation of the module.
        """
        self.log.warning('shamrock_dummy>desactivation')

    def set_center_wavelength(self, center_wavelength):
        """ Set the center wavelength of the spectrometer rotating the grating"""
        self.center_wavelength = center_wavelength

    def get_center_wavelength(self):
        """ Get the center wavelength of the spectrometer """
        return self.center_wavelength

    def get_grating(self):
        """ Get the grating of the spectrometer
        0: 150 lines / mm
        1: 300 lines / mm
        2: 1200 lines / mm """
        return self.grating

    def set_grating(self, grating):
        """ Set the grating of the spectrometer
        0: 150 lines / mm
        1: 300 lines / mm
        2: 1200 lines / mm """
        if 0 <= grating <= 2:
            self.grating = grating
            self.set_wavelength_range(grating)
        else:
            self.log.warning('grating invalid (0: 150 lines / mm, 1: 300 lines / mm, 2: 1200 lines / mm')
        return

    def get_wavelength_range(self):
        """ Get the wavelength range visible on the camera """
        grating = self.get_grating()
        if grating == 0:
            # grating: 150 lines / mm
            return self.get_center_wavelength() - 357/2, self.get_center_wavelength() + 357/2
        elif grating == 1:
            # grating: 300 lines / mm
            return self.get_center_wavelength() - 177 / 2, self.get_center_wavelength() + 177 / 2
        elif grating == 2:
            # grating: 1200 lines / mm
            return self.get_center_wavelength() - 40 / 2, self.get_center_wavelength() + 40 / 2

    def set_wavelength_range(self, grating):
        """ Set the wavelength range visible on the camera corresponding to the grating """
        if grating == 0:
            # grating: 150 lines / mm
            self.wavelength_min = self.get_center_wavelength() - 357/2
            self.wavelength_max = self.get_center_wavelength() + 357/2
        elif grating == 1:
            # grating: 300 lines / mm
            self.wavelength_min = self.get_center_wavelength() - 177 / 2
            self.wavelength_max = self.get_center_wavelength() + 177 / 2
        elif grating == 2:
            # grating: 1200 lines / mm
            self.wavelength_min = self.get_center_wavelength() - 40 / 2
            self.wavelength_max = self.get_center_wavelength() + 40 / 2
        else:
            self.log.warning('grating invalid (0: 150 lines / mm, 1: 300 lines / mm, 2: 1200 lines / mm')
        return
