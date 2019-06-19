# -*- coding: utf-8 -*-
"""
This module operates the graphical user interface of a 2D sample scan placed in a micro cavity

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
    """ The main window for the sample scan GUI """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'sample_scan_gui.ui')

        # Load it
        super(MainWindow, self).__init__()
        uic.loadUi(ui_file, self)
        self.show()


class SampleScanGui(GUIBase):
    """ This is the GUI Class for cavity 2D scan measurements """
    _modclass = 'SampleScanGui'
    _modtype = 'gui'
    # declare QUDI connectors
    sample_scan_logic = Connector(interface='EmptyInterface')
    # signals
    sigAPDsImagesUpdated = QtCore.Signal()

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self._mw = MainWindow()
        self.apd1_image = pg.ImageItem(np.ones([100, 100]), axisOrder='row-major')
        self.apd1_xy_cb = ColorBar(ColorScaleInferno().cmap_normed, 100, 0, 100000)
        self.apd2_image = pg.ImageItem(np.ones([100, 100]), axisOrder='row-major')
        self.apd2_xy_cb = ColorBar(ColorScaleInferno().cmap_normed, 100, 0, 100000)

    def on_activate(self):
        """ Definition, configuration and initialisation of GUI.
        This init connects all the graphic modules, which were created in the
        *.ui file and configures the event handling between the modules.
        """
        # setting up main window
        self._mw = MainWindow()
        # QUDI connectors (can only be declared in on_activate function)
        self._sample_scan_logic = self.sample_scan_logic()
        # configure all the modules of the GUI and connect the different hardware
        self.config_gui()
        # show window
        self._mw.show()
        return

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._mw.close()
        return

    def config_gui(self):
        """ Configure the GUI main window"""
        # values on the gui
        self._mw.xy_scan_range_spinBox.setValue(10)
        self._mw.xy_scan_step_doubleSpinBox.setValue(1)
        self._mw.apd_integration_time_doubleSpinBox.setValue(1)
        # APD1_map
        self.apd1_image = pg.ImageItem(np.ones([100, 100]), axisOrder='row-major')
        self._mw.apd1_xy_ViewWidget.addItem(self.apd1_image)
        self._mw.apd1_xy_ViewWidget.setLabel(axis='bottom', text='x', units='um')
        self._mw.apd1_xy_ViewWidget.setLabel(axis='left', text='y', units='um')
        self.apd1_image.setLookupTable(ColorScaleInferno().lut)
        self.apd1_xy_cb = ColorBar(ColorScaleInferno().cmap_normed, 100, 0, 100000)
        self._mw.apd1_xy_cb_ViewWidget.addItem(self.apd1_xy_cb)
        self._mw.apd1_xy_cb_ViewWidget.hideAxis('bottom')
        self._mw.apd1_xy_cb_ViewWidget.hideAxis('left')
        self._mw.apd1_xy_cb_ViewWidget.setLabel('right', 'Counts', units='counts/s')
        # APD2_map
        self.apd2_image = pg.ImageItem(np.ones([100, 100]), axisOrder='row-major')
        self._mw.apd2_xy_ViewWidget.addItem(self.apd2_image)
        self._mw.apd2_xy_ViewWidget.setLabel(axis='bottom', text='x', units='um')
        self._mw.apd2_xy_ViewWidget.setLabel(axis='left', text='y', units='um')
        self.apd2_image.setLookupTable(ColorScaleInferno().lut)
        self.apd2_xy_cb = ColorBar(ColorScaleInferno().cmap_normed, 100, 0, 100000)
        self._mw.apd2_xy_cb_ViewWidget.addItem(self.apd2_xy_cb)
        self._mw.apd2_xy_cb_ViewWidget.hideAxis('bottom')
        self._mw.apd2_xy_cb_ViewWidget.hideAxis('left')
        self._mw.apd2_xy_cb_ViewWidget.setLabel('right', 'Counts', units='counts/s')
        # connections
        self._mw.xy_scan_pushButton.clicked.connect(self.start_xy_scan)
        self._mw.save_scan_data_pushButton.clicked.connect(self.save_scan_data)
        self._sample_scan_logic.sigUpdateAPDsImages.connect(self.refresh_apds_images, QtCore.Qt.QueuedConnection)
        self._mw.apd1_xy_cb_high_percentile_DoubleSpinBox.valueChanged.connect(self.refresh_apd1_image_per_cent_scale)
        self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.valueChanged.connect(self.refresh_apd1_image_per_cent_scale)
        self._mw.apd2_xy_cb_high_percentile_DoubleSpinBox.valueChanged.connect(self.refresh_apd2_image_per_cent_scale)
        self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.valueChanged.connect(self.refresh_apd2_image_per_cent_scale)
        self._mw.apd1_xy_cb_max_DoubleSpinBox.valueChanged.connect(self.refresh_apd1_image_counts_scale)
        self._mw.apd1_xy_cb_min_DoubleSpinBox.valueChanged.connect(self.refresh_apd1_image_counts_scale)
        self._mw.apd2_xy_cb_max_DoubleSpinBox.valueChanged.connect(self.refresh_apd2_image_counts_scale)
        self._mw.apd2_xy_cb_min_DoubleSpinBox.valueChanged.connect(self.refresh_apd2_image_counts_scale)
        self._mw.apd1_image_reset_pushButton.clicked.connect(self.reset_apd1_image)
        self._mw.apd2_image_reset_pushButton.clicked.connect(self.reset_apd2_image)
        return

    def start_xy_scan(self):
        """ Get the parameters of the scan from the gui and call the scan function in the logic """
        xy_range = self._mw.xy_scan_range_spinBox.value()
        xy_step = self._mw.xy_scan_step_doubleSpinBox.value()
        apd_integration_time = self._mw.apd_integration_time_doubleSpinBox.value()
        self._sample_scan_logic.initialize_snake_scan(xy_range, xy_step, apd_integration_time)
        return

    def refresh_apds_images(self):
        """ Update the current XY image from the logic.
        Everytime a point is scanned, the xy image is rebuild and updated in the GUI """
        self.apd1_image.getViewBox().updateAutoRange()
        self.apd2_image.getViewBox().updateAutoRange()
        # load data from the logic
        apd1_image_data = self._sample_scan_logic.get_apd1_data()
        apd2_image_data = self._sample_scan_logic.get_apd2_data()
        # update the colorbar range for apd1
        if not np.any(apd1_image_data):
            # if all data of apd1 = 0
            apd1_cb_range = [0, 0]
        else:
            # look for min and max among the non zero values data
            apd1_cb_range = [np.min(apd1_image_data[np.nonzero(apd1_image_data)]),
                             np.max(apd1_image_data[np.nonzero(apd1_image_data)])]
            self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.setValue(apd1_cb_range[0] * 100 / apd1_cb_range[1])
            self._mw.apd1_xy_cb_min_DoubleSpinBox.setValue(apd1_cb_range[0])
            self._mw.apd1_xy_cb_max_DoubleSpinBox.setValue(apd1_cb_range[1])
        if apd1_cb_range[0] == apd1_cb_range[1]:
            apd1_cb_range = [np.min(apd1_image_data), np.max(apd1_image_data) + 1]
        # update image and colorbar range for APD1
        self.apd1_image.setImage(image=apd1_image_data, levels=(apd1_cb_range[0], apd1_cb_range[1]))
        self.apd1_xy_cb.refresh_colorbar(apd1_cb_range[0], apd1_cb_range[1])
        # update the colorbar range for APD2
        if not np.any(apd2_image_data):
            # if all data of APD2 = 0
            apd2_cb_range = [0, 0]
        else:
            # look for min and max among the non zero values of data
            apd2_cb_range = [np.min(apd2_image_data[np.nonzero(apd2_image_data)]),
                             np.max(apd2_image_data[np.nonzero(apd2_image_data)])]
            self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.setValue(apd2_cb_range[0] * 100 / apd2_cb_range[1])
            self._mw.apd2_xy_cb_min_DoubleSpinBox.setValue(apd2_cb_range[0])
            self._mw.apd2_xy_cb_max_DoubleSpinBox.setValue(apd2_cb_range[1])
        if apd2_cb_range[0] == apd2_cb_range[1]:
            apd2_cb_range = [np.min(apd2_image_data), np.max(apd2_image_data) + 1]
        # update image and colorbar range for APD2
        self.apd2_image.setImage(image=apd2_image_data, levels=(apd2_cb_range[0], apd2_cb_range[1]))
        self.apd2_xy_cb.refresh_colorbar(apd2_cb_range[0], apd2_cb_range[1])
        self._sample_scan_logic.continue_snake_scan()
        return

    def save_scan_data(self):
        """ Call the function in the logic that save the data of the 2D / 3D scans"""
        self._sample_scan_logic.save_snake_scan_data()
        return

    def reset_apd1_image(self):
        """ Reset APD1 image and colorbar range on the gui"""
        # load APD1 data from the logic
        apd1_image_data = self._sample_scan_logic.get_apd1_data()
        # get the range of APD1 data
        apd1_cb_range = [np.min(apd1_image_data), np.max(apd1_image_data)]
        # reset range values of the % and counts scale on the gui
        self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.setValue(apd1_cb_range[0] * 100 / apd1_cb_range[1])
        self._mw.apd1_xy_cb_high_percentile_DoubleSpinBox.setValue(100)
        self._mw.apd1_xy_cb_min_DoubleSpinBox.setValue(apd1_cb_range[0])
        self._mw.apd1_xy_cb_max_DoubleSpinBox.setValue(apd1_cb_range[1])
        # reset image and colorbar on the gui
        self.apd1_image.setImage(image=apd1_image_data, levels=(apd1_cb_range[0], apd1_cb_range[1]))
        self.apd1_xy_cb.refresh_colorbar(apd1_cb_range[0], apd1_cb_range[1])
        return

    def reset_apd2_image(self):
        """ Reset APD2 image and colorbar range on the gui"""
        # load APD2 data from the logic
        apd2_image_data = self._sample_scan_logic.get_apd2_data()
        # get the range of APD2 data
        apd2_cb_range = [np.min(apd2_image_data), np.max(apd2_image_data)]
        # reset range values of the % and counts scale on the gui
        self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.setValue(apd2_cb_range[0] * 100 / apd2_cb_range[1])
        self._mw.apd2_xy_cb_high_percentile_DoubleSpinBox.setValue(100)
        self._mw.apd2_xy_cb_min_DoubleSpinBox.setValue(apd2_cb_range[0])
        self._mw.apd2_xy_cb_max_DoubleSpinBox.setValue(apd2_cb_range[1])
        # reset image and colorbar on the gui
        self.apd2_image.setImage(image=apd2_image_data, levels=(apd2_cb_range[0], apd2_cb_range[1]))
        self.apd2_xy_cb.refresh_colorbar(apd2_cb_range[0], apd2_cb_range[1])
        return

    def refresh_apd1_image_per_cent_scale(self):
        """ Refresh the image APD1 on the gui when % scale is modified """
        # load APD1 data from the logic
        apd1_image_data = self._sample_scan_logic.get_apd1_data()
        # define the range using the values on the gui
        apd1_cb_range = [self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.value(),
                         self._mw.apd1_xy_cb_high_percentile_DoubleSpinBox.value()]
        # if min range > max range
        if apd1_cb_range[0] > apd1_cb_range[1]:
            apd1_cb_range[0] = apd1_cb_range[1] - 1 / 100
            self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.setValue(apd1_cb_range[0])
        # update values of the counts range
        apd1_cb_range[0] = apd1_cb_range[0] * np.max(apd1_image_data) / 100
        apd1_cb_range[1] = apd1_cb_range[1] * np.max(apd1_image_data) / 100
        self._mw.apd1_xy_cb_min_DoubleSpinBox.setValue(apd1_cb_range[0])
        self._mw.apd1_xy_cb_max_DoubleSpinBox.setValue(apd1_cb_range[1])
        return

    def refresh_apd1_image_counts_scale(self):
        """ Refresh the image APD1 on the gui when counts scale is modified """
        # load APD1 data from the logic
        apd1_image_data = self._sample_scan_logic.get_apd1_data()
        # if counts scale is chosen
        apd1_cb_range = [self._mw.apd1_xy_cb_min_DoubleSpinBox.value(),
                         self._mw.apd1_xy_cb_max_DoubleSpinBox.value()]
        # if min range > max range
        if apd1_cb_range[0] > apd1_cb_range[1]:
            apd1_cb_range[0] = apd1_cb_range[1] - 1
            self._mw.apd1_xy_cb_min_DoubleSpinBox.setValue(apd1_cb_range[0])
        # update values of the percentage range
        self._mw.apd1_xy_cb_low_percentile_DoubleSpinBox.setValue(apd1_cb_range[0] / np.max(apd1_image_data) * 100)
        self._mw.apd1_xy_cb_high_percentile_DoubleSpinBox.setValue(apd1_cb_range[1] / np.max(apd1_image_data) * 100)
        self.apd1_image.setImage(image=apd1_image_data, levels=(apd1_cb_range[0], apd1_cb_range[1]))
        self.apd1_xy_cb.refresh_colorbar(apd1_cb_range[0], apd1_cb_range[1])
        return

    def refresh_apd2_image_per_cent_scale(self):
        """ Refresh the image APD2 on the gui when % scale is modified """
        # load APD2 data from the logic
        apd2_image_data = self._sample_scan_logic.get_apd2_data()
        # define the range using the values on the gui
        apd2_cb_range = [self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.value(),
                         self._mw.apd2_xy_cb_high_percentile_DoubleSpinBox.value()]
        # if min range > max range
        if apd2_cb_range[0] > apd2_cb_range[1]:
            apd2_cb_range[0] = apd2_cb_range[1] - 1 / 100
            self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.setValue(apd2_cb_range[0])
        # update values of the counts range
        apd2_cb_range[0] = apd2_cb_range[0] * np.max(apd2_image_data) / 100
        apd2_cb_range[1] = apd2_cb_range[1] * np.max(apd2_image_data) / 100
        self._mw.apd2_xy_cb_min_DoubleSpinBox.setValue(apd2_cb_range[0])
        self._mw.apd2_xy_cb_max_DoubleSpinBox.setValue(apd2_cb_range[1])
        return

    def refresh_apd2_image_counts_scale(self):
        """ Refresh the image APD2 on the gui when counts scale is modified """
        # load APD2 data from the logic
        apd2_image_data = self._sample_scan_logic.get_apd2_data()
        # if counts scale is chosen
        apd2_cb_range = [self._mw.apd2_xy_cb_min_DoubleSpinBox.value(),
                         self._mw.apd2_xy_cb_max_DoubleSpinBox.value()]
        # if min range > max range
        if apd2_cb_range[0] > apd2_cb_range[1]:
            apd2_cb_range[0] = apd2_cb_range[1] - 1
            self._mw.apd2_xy_cb_min_DoubleSpinBox.setValue(apd2_cb_range[0])
        # update values of the percentage range
        self._mw.apd2_xy_cb_low_percentile_DoubleSpinBox.setValue(apd2_cb_range[0] / np.max(apd2_image_data) * 100)
        self._mw.apd2_xy_cb_high_percentile_DoubleSpinBox.setValue(apd2_cb_range[1] / np.max(apd2_image_data) * 100)
        self.apd2_image.setImage(image=apd2_image_data, levels=(apd2_cb_range[0], apd2_cb_range[1]))
        self.apd2_xy_cb.refresh_colorbar(apd2_cb_range[0], apd2_cb_range[1])
        return
