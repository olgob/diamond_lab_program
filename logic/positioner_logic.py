# -*- coding: utf-8 -*-
"""
This module operates a nano positioner.

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

from logic.generic_logic import GenericLogic
from core.module import Connector
from qtpy import QtCore
import datetime
import os


class PositionerLogic(GenericLogic):
    """
    This is the Logic class for a positioner stage.
    """
    _modclass = 'JPE_CPSHR3_logic'
    _modtype = 'logic'

    # Declaration of signals
    sig_next_cmd_line = QtCore.Signal()
    sigUpdateTrackingLogic = QtCore.Signal()

    # declare qudi connectors
    positioner = Connector(interface='EmptyInterface')
    savelogic = Connector(interface='SaveLogic')

    def __init__(self, config, **kwargs):
        """ Initialize the class """
        super().__init__(config=config, **kwargs)
        # update the tracking on the gui
        self.x_tracking, self.y_tracking, self.z_tracking = self.open_positioners_tracking_file()
        self.sigUpdateTrackingLogic.emit()

    def on_activate(self):
        """ Initialisation performed during activation of the module"""
        # initialize qudi connectors
        self._positioner_hardware = self.positioner()
        self._save_logic = self.savelogic()
        # signal connection
        self._positioner_hardware.sigUpdateTracking.connect(self.update_tracking)

    def write_positioners_tracking_file(self, x, y, z):
        """" Write the tracking position [X, Y, Z] in a .txt file"""
        path = r"C:\Users\olgob\Desktop\qudi_diamond_lab"
        name_file = "positioner_tracking.txt"
        tracking_file_path = os.path.join(path, name_file)
        try:
            tracking_file = open(tracking_file_path, "a")
            tracking_file.write("%s %f %f %f\n" % (datetime.datetime.now(), x, y, z))
            # tracking_file.close()
        except FileNotFoundError:
            print("file \" %s \" do not exist... Impossible to save positioner tracking" % name_file)
        return

    def open_positioners_tracking_file(self):
        """" Read the tracking position [X, Y, Z] in a .txt file"""
        path = r"C:\Users\olgob\Desktop\qudi_diamond_lab"
        filename = "positioner_tracking.txt"
        tracking_file_path = os.path.join(path, filename)
        try:
            tracking_file = open(tracking_file_path, "r")
            last_line = tracking_file.readlines()[-1].split(" ")
        except FileNotFoundError:
            print("file \" %s \" do not exist... creating file" % filename)
            tracking_file = open(tracking_file_path, "w")
            initial_line = str(datetime.datetime.now()) + " 0.0 0.0 0.0"
            tracking_file.write(initial_line)
            tracking_file.close()
            tracking_file = open(tracking_file_path, "r")
            last_line = tracking_file.readlines()[0].split(" ")
            print(last_line)
        x_start = float(last_line[2])
        y_start = float(last_line[3])
        z_start = float(last_line[4])
        return x_start, y_start, z_start

    def on_deactivate(self):
        """ Reverse steps of activation """
        self.stop_positioner()
        return

    def move_xyz(self, x, y, z):
        """ Move the positioners to move the sample in XYZ """
        self._positioner_hardware.move_xyz(x, y, z)
        return

    def set_temperature(self, temperature):
        """ Set temperature of the positioners """
        self._positioner_hardware.set_temperature(temperature)
        return

    def get_temperature(self):
        """ Get temperature of the positioners """
        return self._positioner_hardware.get_temperature()

    def set_frequency(self, frequency):
        """ Set frequency of the positioners """
        self._positioner_hardware.set_frequency(frequency)
        return

    def get_frequency(self):
        """ Get frequency of the positioners """
        return self._positioner_hardware.get_frequency()

    def set_step_size(self, step_size):
        """ Set step size of the positioners """
        self._positioner_hardware.set_step_size(step_size)
        return

    def get_step_size(self):
        """ Get step size of the positioners """
        return self._positioner_hardware.get_step_size()

    def move_positioner_1(self, displacement):
        """ Move the positioner 1 by the desired displacement """
        self._positioner_hardware.move_positioner_1(displacement)
        return

    def move_positioner_2(self, displacement):
        """ Move the positioner 2 by the desired displacement """
        self._positioner_hardware.move_positioner_2(displacement)
        return

    def move_positioner_3(self, displacement):
        """ Move the positioner 3 by the desired displacement """
        self._positioner_hardware.move_positioner_3(displacement)
        return

    def stop_positioner(self):
        """ Stop the positioners """
        self._positioner_hardware.stop_positioner()
        return

    def update_x_tracking(self, x_tracking):
        """ Update the X tracking value """
        self.x_tracking += x_tracking
        return

    def update_y_tracking(self, y_tracking):
        """ Update the Y tracking value """
        self.y_tracking += y_tracking
        return

    def update_z_tracking(self, z_tracking):
        """ Update the Z tracking value """
        self.z_tracking += z_tracking
        return

    def set_x_tracking(self, x_tracking):
        """ Set the X tracking value """
        self.x_tracking = x_tracking
        return

    def set_y_tracking(self, y_tracking):
        """ Set the Y tracking value """
        self.y_tracking = y_tracking
        return

    def set_z_tracking(self, z_tracking):
        """ Set the Z tracking value """
        self.z_tracking = z_tracking
        return

    def get_x_tracking(self):
        """ Get the X tracking value """
        return self.x_tracking

    def get_y_tracking(self):
        """ Get the Y tracking value """
        return self.y_tracking

    def get_z_tracking(self):
        """ Get the Z tracking value """
        return self.z_tracking

    def reset_tracking_x(self):
        """ Reset the X tracking value """
        self.x_tracking = 0
        self.sigUpdateTrackingLogic.emit()
        return

    def reset_tracking_y(self):
        """ Reset the Y tracking value """
        self.y_tracking = 0
        self.sigUpdateTrackingLogic.emit()
        return

    def reset_tracking_z(self):
        """ Reset the Z tracking value """
        self.z_tracking = 0
        self.sigUpdateTrackingLogic.emit()
        return

    def update_tracking(self):
        """ Update the tracking values """
        self.update_x_tracking(self._positioner_hardware.x_tracking)
        self.update_y_tracking(self._positioner_hardware.y_tracking)
        self.update_z_tracking(self._positioner_hardware.z_tracking)
        self.write_positioners_tracking_file(self.get_x_tracking() * 1e6, self.get_y_tracking() * 1e6,
                                             self.get_z_tracking() * 1e6)
        self.sigUpdateTrackingLogic.emit()
        return

