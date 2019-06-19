# -*- coding: utf-8 -*-
"""
This module operates the graphical user interface of a cavity stability measurement and non linearity measurement

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

import os
from core.module import Connector
from gui.guibase import GUIBase
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic
import pyqtgraph as pg
import numpy as np
from gui.colordefs import ColorScaleInferno
from gui.guiutils import ColorBar


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window for the cavity stability measurement and non linearity measurement GUI.
    """

    def __init__(self):
        # inheritance
        super(MainWindow, self).__init__()
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'cavity_stability_measurement_gui.ui')
        uic.loadUi(ui_file, self)
        self.show()


class CavityStabilityMeasurementGui(GUIBase):
    """
    This is the GUI Class for WLT measurements
    """
    _modclass = 'CavityStabilityMeasurement'
    _modtype = 'gui'

    # declare connectors
    cavity_stability_measurement_logic = Connector(interface='EmptyInterface')
    sigContinueDriftMeasurement = QtCore.Signal()

    def on_activate(self):
        """ Definition, configuration and initialisation of the PZT_NL_CAVITY_DRIFT GUI.
        This init connects all the graphic modules, which were created in the
        *.ui file and configures the event handling between the modules """
        # setting up main window
        self._mw = MainWindow()
        self._cavity_stability_measurement_logic = self.cavity_stability_measurement_logic()
        # configure the gui
        self.config_gui()
        # show window
        self._mw.show()

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._mw.close()
        return

    def config_gui(self):
        """ Configure the GUI values and make connections to functions """
        # configure values on the gui
        self._mw.cavity_drift_acquisition_rate_spinBox.setValue(
            self._cavity_stability_measurement_logic.get_cavity_drift_acquisition_rate())
        self._mw.cavity_drift_measurement_time_spinBox.setValue(
            self._cavity_stability_measurement_logic.get_cavity_drift_measurement_time())
        # configure the 2 plot widgets
        self.config_2d_spectrum()
        # Qt connections
        self._mw.spectrum_2d_save_data_pushButton.clicked.connect(self._cavity_stability_measurement_logic.save_spectrum_2d_data)
        self._mw.cavity_drift_start_pushButton.clicked.connect(self.start_cavity_drift_measurement)
        self._cavity_stability_measurement_logic.sigUpdate2DSpectrum.connect(self.update_spectrum_2d, QtCore.Qt.QueuedConnection)
        self._mw.spectrum_2d_cb_low_percentile_DoubleSpinBox.valueChanged.connect(
            self.refresh_spectrum_2d_image_per_cent_scale)
        self._mw.spectrum_2d_cb_high_percentile_DoubleSpinBox.valueChanged.connect(
            self.refresh_spectrum_2d_image_per_cent_scale)
        self._mw.spectrum_2d_cb_min_DoubleSpinBox.valueChanged.connect(self.refresh_spectrum_2d_image_counts_scale)
        self._mw.spectrum_2d_cb_max_DoubleSpinBox.valueChanged.connect(self.refresh_spectrum_2d_image_counts_scale)
        self._mw.nl_start_pushButton.clicked.connect(self.start_non_linearity_measurement)

    def config_2d_spectrum(self):
        """ Configure the 2D spectrum plot widget """
        # creation of an image item that is filled with the collected data
        self.spectrum_2d_image = pg.ImageItem(self._cavity_stability_measurement_logic.spectrum_2d_data, axisOrder='row-major')
        # add the image item to the ViewWidget, which was defined in the UI file.
        self._mw.spectrum_2d_PlotWidget.addItem(self.spectrum_2d_image)
        # configure the plotWidget
        self._mw.spectrum_2d_PlotWidget.setLabel(axis='bottom', text='Camera pixel', units='')
        self._mw.spectrum_2d_PlotWidget.setLabel(axis='left', text='Acquisition', units='')
        # get the color scales LUT
        self.spectrum_2d_image.setLookupTable(ColorScaleInferno().lut)
        # configure the Colorbar
        self.spectrum_2d_cb = ColorBar(ColorScaleInferno().cmap_normed, 100, 0, 100000)
        # adding color bar to ViewWidget
        self._mw.spectrum_2d_cb_PlotWidget.addItem(self.spectrum_2d_cb)
        self._mw.spectrum_2d_cb_PlotWidget.hideAxis('bottom')
        self._mw.spectrum_2d_cb_PlotWidget.hideAxis('left')
        self._mw.spectrum_2d_cb_PlotWidget.setLabel('right', 'Counts', units='counts/s')
        return

    def start_cavity_drift_measurement(self):
        """ Start the cavity drift measurement """
        # get parameters from the gui
        acquisition_rate = self._mw.cavity_drift_acquisition_rate_spinBox.value()
        measurement_time = self._mw.cavity_drift_measurement_time_spinBox.value()
        # change parameters in the logic
        self._cavity_stability_measurement_logic.set_cavity_drift_acquisition_rate(acquisition_rate)
        self._cavity_stability_measurement_logic.set_cavity_drift_measurement_time(measurement_time)
        # start drift measurement in the logic with the updated parameters
        self._cavity_stability_measurement_logic.initialize_cavity_drift_measurement()
        return

    def start_non_linearity_measurement(self):
        """ Start the non linearity measurement """
        # get parameters from the gui
        voltage_start = self._mw.start_voltage_doubleSpinBox.value()
        voltage_stop = self._mw.stop_voltage_doubleSpinBox.value()
        voltage_steps = self._mw.number_of_steps_doubleSpinBox.value()
        voltages_list = np.linspace(voltage_start, voltage_stop, voltage_steps)
        # set the voltage list to apply to the scanner in the logic
        self._cavity_stability_measurement_logic.set_scanner_voltages_list(voltages_list)
        # change parameters in the logic
        # start non linearity measurement in the logic with the updated parameters
        self._cavity_stability_measurement_logic.initialize_non_linearity_measurement()
        return

    def update_spectrum_2d(self):
        """ Update the current spectrum 2D image from the logic.
        Every time spectrum acquired, the spectrum 2D image image is rebuild and updated in the GUI """
        self.spectrum_2d_image.getViewBox().updateAutoRange()
        # load data from the logic
        spectrum_2d_data = self._cavity_stability_measurement_logic.get_spectrum_2d_data()
        # update the colorbar range for 2D spectrum
        if not np.any(spectrum_2d_data):
            # if all data of apd1 = 0
            spectrum_2d_cb_range = [0, 0]
        else:
            # look for min and max among the non zero values data
            spectrum_2d_cb_range = [np.min(spectrum_2d_data[np.nonzero(spectrum_2d_data)]),
                                    np.max(spectrum_2d_data[np.nonzero(spectrum_2d_data)])]
            self._mw.spectrum_2d_cb_low_percentile_DoubleSpinBox.setValue(
                spectrum_2d_cb_range[0] * 100 / spectrum_2d_cb_range[1])
            self._mw.spectrum_2d_cb_min_DoubleSpinBox.setValue(spectrum_2d_cb_range[0])
            self._mw.spectrum_2d_cb_max_DoubleSpinBox.setValue(spectrum_2d_cb_range[1])
        if spectrum_2d_cb_range[0] == spectrum_2d_cb_range[1]:
            spectrum_2d_cb_range = [np.min(spectrum_2d_data), np.max(spectrum_2d_data) + 1]
        # update image and colorbar range for 2D spectrum
        self.spectrum_2d_image.setImage(image=spectrum_2d_data,
                                        levels=(spectrum_2d_cb_range[0], spectrum_2d_cb_range[1]))
        self.spectrum_2d_cb.refresh_colorbar(spectrum_2d_cb_range[0], spectrum_2d_cb_range[1])
        return

    def refresh_spectrum_2d_image_per_cent_scale(self):
        """ Refresh the 2D spectrum image on the gui when % scale is modified """
        # load 2D spectrum data from the logic
        spectrum_2d_data = self._cavity_stability_measurement_logic.get_spectrum_2d_data()
        # define the range using the values on the gui
        spectrum_2d_cb_range = [self._mw.spectrum_2d_cb_low_percentile_DoubleSpinBox.value(),
                                self._mw.spectrum_2d_cb_high_percentile_DoubleSpinBox.value()]
        # if min range > max range
        if spectrum_2d_cb_range[0] > spectrum_2d_cb_range[1]:
            spectrum_2d_cb_range[0] = spectrum_2d_cb_range[1] - 1 / 100
            self._mw.spectrum_2d_cb_low_percentile_DoubleSpinBox.setValue(spectrum_2d_cb_range[0])
        # update values of the counts range
        spectrum_2d_cb_range[0] = spectrum_2d_cb_range[0] * np.max(spectrum_2d_data) / 100
        spectrum_2d_cb_range[1] = spectrum_2d_cb_range[1] * np.max(spectrum_2d_data) / 100
        self._mw.spectrum_2d_cb_min_DoubleSpinBox.setValue(spectrum_2d_cb_range[0])
        self._mw.spectrum_2d_cb_max_DoubleSpinBox.setValue(spectrum_2d_cb_range[1])
        return

    def refresh_spectrum_2d_image_counts_scale(self):
        """ Refresh the spectrum 2D image on the gui when counts scale is modified """
        # load spectrum 2D data from the logic
        spectrum_2d_data = self._cavity_stability_measurement_logic.get_spectrum_2d_data()
        # if counts scale is chosen
        spectrum_2d_cb_range = [self._mw.spectrum_2d_cb_min_DoubleSpinBox.value(),
                                self._mw.spectrum_2d_cb_max_DoubleSpinBox.value()]
        # if min range > max range
        if spectrum_2d_cb_range[0] > spectrum_2d_cb_range[1]:
            spectrum_2d_cb_range[0] = spectrum_2d_cb_range[1] - 1
            self._mw.spectrum_2d_cb_min_DoubleSpinBox.setValue(spectrum_2d_cb_range[0])
        # update values of the percentage range
        self._mw.spectrum_2d_cb_low_percentile_DoubleSpinBox.setValue(
            spectrum_2d_cb_range[0] / np.max(spectrum_2d_data) * 100)
        self._mw.spectrum_2d_cb_high_percentile_DoubleSpinBox.setValue(
            spectrum_2d_cb_range[1] / np.max(spectrum_2d_data) * 100)
        self.spectrum_2d_image.setImage(image=spectrum_2d_data,
                                        levels=(spectrum_2d_cb_range[0], spectrum_2d_cb_range[1]))
        self.spectrum_2d_cb.refresh_colorbar(spectrum_2d_cb_range[0], spectrum_2d_cb_range[1])
        return

    def save_data(self):
        """ Save data of the 2D spectrum """
        pass
