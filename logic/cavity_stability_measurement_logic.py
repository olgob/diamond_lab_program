# -*- coding: utf-8 -*-
"""
This module operates a cavity stability measurement and characterize the non linearity of cavity

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

from core.module import Connector
from gui.guibase import GUIBase
from qtpy import QtCore
import numpy as np
import time


class CavityStabilityMeasurementLogic(GUIBase):
    """
    This is the GUI Class for Cavity Drift and Non Linearity Measurement
    """
    _modclass = 'CavityStabilityMeasurementLogic'
    _modtype = 'logic'

    # declare connectors
    spectrometer_logic = Connector(interface='EmptyInterface')
    acquisition_card_logic = Connector(interface='EmptyInterface')

    # signals
    sigUpdate2DSpectrum = QtCore.Signal()
    sigContinueDriftMeasurement = QtCore.Signal()
    sigContinueNonLinearityMeasurement = QtCore.Signal()

    def __init__(self, **kwargs):
        """ Initialize class """
        super().__init__(**kwargs)
        # declare variables
        self.cavity_drift_acquisition_rate = 1  # acquisition rate of the drift measurement [/min]
        self.cavity_drift_measurement_time = 1  # measurement time of the drift measurement [min]
        self.cavity_drift_acquisitions_number = self.cavity_drift_acquisition_rate * self.cavity_drift_measurement_time
        self.drift_measurement_iteration = 0  # iteration number of the drift measurement
        self.non_linearity_measurement_iteration = 0  # iteration number of the non linearity measurement
        self.spectrum_2d_data = np.zeros([100, 100])  # 2D spectrum data
        self.scanner_voltages_list = np.zeros(100)  # successive voltages applied on the scanner for NL measurement

    def on_activate(self):
        """ Connect QUDI modules """
        self._spectrometer_logic = self.spectrometer_logic()
        self._acquisition_card_logic = self.acquisition_card_logic()

        self.sigContinueDriftMeasurement.connect(self.continue_cavity_drift_measurement, QtCore.Qt.QueuedConnection)
        self.sigContinueNonLinearityMeasurement.connect(self.continue_non_linearity_measurement,
                                                        QtCore.Qt.QueuedConnection)

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._spectrometer_logic.on_desactivate()
        return

    def set_cavity_drift_acquisition_rate(self, cavity_drift_acquisition_rate):
        """ Set the acquisition rate (/min) of the cavity drift measurement """
        self.cavity_drift_acquisition_rate = cavity_drift_acquisition_rate
        return

    def get_cavity_drift_acquisition_rate(self):
        """ Get the acquisition rate (/min) of the cavity drift measurement """
        return self.cavity_drift_acquisition_rate

    def set_cavity_drift_measurement_time(self, cavity_drift_measurement_time):
        """ Set the total measurement time of the cavity drift measurement """
        self.cavity_drift_measurement_time = cavity_drift_measurement_time
        return

    def get_cavity_drift_measurement_time(self):
        """ Get the total measurement time of the cavity drift measurement """
        return self.cavity_drift_measurement_time

    def set_cavity_drift_acquisitions_number(self, cavity_drift_acquisitions_number):
        """ Set the total measurement time of the cavity drift measurement """
        self.cavity_drift_acquisitions_number = cavity_drift_acquisitions_number
        return

    def get_total_iterations_number_drift(self):
        """ Get the total number of iteration of the measurement """
        return int(self.get_cavity_drift_acquisition_rate() * self.get_cavity_drift_measurement_time())

    def get_total_iterations_number_nl(self):
        """ Get the total number of iteration of the measurement """
        return int(len(self.get_scanner_voltages_list()))

    def set_scanner_voltages_list(self, voltages_list):
        """ Set the volatges list to apply to the scanner during a non linearity measurement"""
        self.scanner_voltages_list = voltages_list
        return

    def get_scanner_voltages_list(self):
        """ get the volatges list to apply to the scanner during a non linearity measurement"""
        return self.scanner_voltages_list

    def get_spectrum_2d_data(self):
        """ Get the data of the 2D spectrum """
        return self.spectrum_2d_data

    def initialize_cavity_drift_measurement(self):
        """Start the white light transmission measurement"""
        # prepare the 2d spectrum image
        self.spectrum_2d_data = np.zeros(
            [self.get_total_iterations_number_drift(), self._spectrometer_logic.get_camera_size()[0]])
        self.drift_measurement_iteration = 0
        self.spectrum_2d_data[self.drift_measurement_iteration, :] = self._spectrometer_logic.take_spectrum_data()
        self.drift_measurement_iteration += 1
        self.sigUpdate2DSpectrum.emit()
        time.sleep(60 / self.get_cavity_drift_acquisition_rate())
        self.sigContinueDriftMeasurement.emit()
        return

    def continue_cavity_drift_measurement(self):
        """Continue the cavity drift measurement"""
        if self.drift_measurement_iteration < self.get_total_iterations_number_drift():
            self.spectrum_2d_data[self.drift_measurement_iteration, :] = self._spectrometer_logic.take_spectrum_data()
            self.drift_measurement_iteration += 1
            self.sigUpdate2DSpectrum.emit()
            # wait between starting next acquisition a time corresponding to acquisition rate
            time.sleep(60 / self.cavity_drift_acquisition_rate)
            # call again the function for the next acquisition
            self.sigContinueDriftMeasurement.emit()
        return

    def initialize_non_linearity_measurement(self):
        """Start the non linearity measurement"""
        # prepare the 2d spectrum image
        self.spectrum_2d_data = np.zeros(
            [self.get_total_iterations_number_nl(), self._spectrometer_logic.get_camera_size()[0]])
        self.non_linearity_measurement_iteration = 0
        self.spectrum_2d_data[self.non_linearity_measurement_iteration,
                              :] = self._spectrometer_logic.take_spectrum_data()
        # change the length on the cavity applying a voltage on the scanner
        self._acquisition_card_logic.start_offset(self.get_scanner_voltages_list()[self.non_linearity_measurement_iteration])
        # iterate for the next loop
        self.non_linearity_measurement_iteration += 1
        # update gui
        self.sigUpdate2DSpectrum.emit()
        # call continue_non_linearity_measurement function with a signal
        self.sigContinueNonLinearityMeasurement.emit()
        return

    def continue_non_linearity_measurement(self):
        """Continue the cavity drift measurement"""
        if self.non_linearity_measurement_iteration < self.get_total_iterations_number_nl():
            self.spectrum_2d_data[self.non_linearity_measurement_iteration,
                                  :] = self._spectrometer_logic.take_spectrum_data()
            # change the length on the cavity applying a voltage on the scanner
            self._acquisition_card_logic.start_offset(
                self.get_scanner_voltages_list()[self.non_linearity_measurement_iteration])
            # iterate for the next loop
            self.non_linearity_measurement_iteration += 1
            # update gui
            self.sigUpdate2DSpectrum.emit()
            # call again continue_non_linearity_measurement function with a signal
            self.sigContinueNonLinearityMeasurement.emit()
        return

    def get_wavelengths(self):
        """ Get the wavelengths scale of the spectrum """
        return self._spectrometer_logic.get_wavelengths()

    def save_spectrum_2d_data(self):
        """ Save 2D spectrum data """
        pass
