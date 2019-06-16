import os
from core.module import Connector
from gui.guibase import GUIBase
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic
import pyqtgraph as pg
import numpy as np
from gui.colordefs import QudiPalettePale as palette


class MainWindow(QtWidgets.QMainWindow):
    """ The main window for the spectrometer GUI """

    def __init__(self, **kwargs):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'spectrometer_gui.ui')

        # Load it
        super(MainWindow, self).__init__(**kwargs)
        uic.loadUi(ui_file, self)
        self.show()


class SpectrometerGui(GUIBase):
    """
    This is the GUI Class for WLT measurements
    """
    _modclass = 'SpectrometerGui'
    _modtype = 'gui'

    # declare connectors
    # scanner_logic = Connector(interface='EmptyInterface')
    spectrometer_logic = Connector(interface='EmptyInterface')
    sigContinueTakeSpectrum = QtCore.Signal()

    def on_activate(self):
        """ Definition, configuration and initialisation of the ODMR GUI.
        This init connects all the graphic modules, which were created in the
        *.ui file and configures the event handling between the modules.
        """
        # setting up main window
        self._mw = MainWindow()
        self._spectrometer_logic = self.spectrometer_logic()
        # configure the gui values
        self.config_spectrometer()
        # show window
        self._mw.show()

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._mw.close()
        return

    def config_spectrometer(self):
        # configure values on the gui loading them from the logic
        self._mw.set_temperature_doubleSpinBox.setValue(self._spectrometer_logic.get_camera_temperature())
        self._mw.number_of_accumulations_doubleSpinBox.setValue(
            self._spectrometer_logic.get_camera_number_accumulations())
        self._mw.set_wavelength_doubleSpinBox.setValue(self._spectrometer_logic.get_center_wavelength())
        self._mw.exposure_time_doubleSpinBox.setValue(self._spectrometer_logic.get_camera_exposure_time())
        self._mw.cycle_time_doubleSpinBox.setValue(self._spectrometer_logic.get_camera_cycle_time())
        self._mw.grating_spinBox.setValue(self._spectrometer_logic.get_grating())
        self._mw.spectrum_xmin_spinBox.setValue(self._spectrometer_logic.get_wavelength_range()[0])
        self._mw.spectrum_ymin_spinBox.setValue(self._spectrometer_logic.get_wavelength_range()[1])

        # configure the 1D spectrum plot widget
        self.config_1d_spectrum_plot_widget()

        # Qt connections
        self._mw.spectrum_save_data_pushButton.clicked.connect(self._spectrometer_logic.save_spectrum_data)
        self._mw.take_background_pushButton.clicked.connect(self._spectrometer_logic.set_background_data)
        self._mw.reset_background_pushButton.clicked.connect(self._spectrometer_logic.reset_background_data)
        self._mw.take_spectrum_pushButton.clicked.connect(self.take_spectrum_data)
        self._mw.number_of_accumulations_doubleSpinBox.editingFinished.connect(self.set_accumulation_number)
        self._mw.exposure_time_doubleSpinBox.editingFinished.connect(self.set_exposure_time)
        self._mw.cycle_time_doubleSpinBox.editingFinished.connect(self.set_cycle_time)
        self._mw.set_temperature_pushButton.clicked.connect(self.set_temperature)
        self._mw.set_wavelength_doubleSpinBox.editingFinished.connect(self.set_center_wavelength)
        self._spectrometer_logic.sigSpectrum1DUpdate.connect(self.update_spectrum_1d, QtCore.Qt.QueuedConnection)
        self._mw.grating_spinBox.editingFinished.connect(self.set_grating)
        self.sigContinueTakeSpectrum.connect(self.take_spectrum_data, QtCore.Qt.QueuedConnection)
        return

    def config_1d_spectrum_plot_widget(self):
        """ Configure the 1D spectrum plot widget """
        # get the wavelengths and the counts values from the logic and generate a plot data item
        self.spectrum_image = pg.PlotDataItem(self._spectrometer_logic.get_wavelengths(),
                                              self._spectrometer_logic.get_spectrum_data(),
                                              pen=pg.mkPen(palette.c1, style=QtCore.Qt.DotLine),
                                              symbol=None,
                                              symbolPen=palette.c1,
                                              symbolBrush=palette.c1,
                                              symbolSize=7)
        # put this plot data item into the plot widget of the gui
        self._mw.spectrum_PlotWidget.addItem(self.spectrum_image)
        # configure axis of the plot
        self._mw.spectrum_PlotWidget.setLabel(axis='left', text='Counts', units='Counts/s')
        self._mw.spectrum_PlotWidget.setLabel(axis='bottom', text='Wavelength', units='nm')
        self._mw.spectrum_PlotWidget.showGrid(x=True, y=True, alpha=0.8)
        return

    def set_accumulation_number(self):
        accumulation_number = self._mw.number_of_accumulations_doubleSpinBox.value()
        self._spectrometer_logic.set_camera_number_accumulations(accumulation_number)
        return

    def set_exposure_time(self):
        exposure_time = self._mw.exposure_time_doubleSpinBox.value()
        self._spectrometer_logic.set_camera_exposure_time(exposure_time)
        return

    def set_cycle_time(self):
        cycle_time = self._mw.cycle_time_doubleSpinBox.value()
        self._spectrometer_logic.set_camera_cycle_time(cycle_time)
        return

    def set_temperature(self):
        # get temperature value from the gui
        temperature = self._mw.set_temperature_doubleSpinBox.value()
        # set new temperature value in the logic
        self._spectrometer_logic.set_camera_temperature(temperature)
        return

    def update_spectrum_1d(self):
        """ Update the current 1D spectrum from the logic """
        data = self._spectrometer_logic.get_spectrum_data()
        if self._mw.spectrum_autorange_radioButton.isChecked():
            # load x_min, x_max, y_min, y_max, values from the logic
            x_min, x_max = self._spectrometer_logic.get_wavelength_range()
            y_min = np.min(self._spectrometer_logic.get_spectrum_data())
            y_max = np.max(self._spectrometer_logic.get_spectrum_data())
            # update values on the gui
            self._mw.spectrum_xmin_spinBox.setValue(x_min)
            self._mw.spectrum_xmax_spinBox.setValue(x_max)
            self._mw.spectrum_ymin_spinBox.setValue(y_min)
            self._mw.spectrum_ymax_spinBox.setValue(y_max)
            # update the range of the gui plot widget
            self.spectrum_image.getViewBox().setRange(xRange=(x_min, x_max),
                                                      yRange=(y_min, y_max),
                                                      update=True,
                                                      disableAutoRange=False)
        else:
            # load x_min, x_max, y_min, y_max, values from the gui
            x_min = self._mw.spectrum_xmin_spinBox.value()
            x_max = self._mw.spectrum_xmax_spinBox.value()
            y_min = self._mw.spectrum_ymin_spinBox.value()
            y_max = self._mw.spectrum_ymax_spinBox.value()
            # update the range of the gui plot widget
            self.spectrum_image.getViewBox().setRange(xRange=(x_min, x_max),
                                                      yRange=(y_min, y_max),
                                                      update=True,
                                                      disableAutoRange=True)
        # update the data of the gui plot widget taking the data from the logic
        self.spectrum_image.setData(x=self._spectrometer_logic.get_wavelengths(), y=data)
        return

    def take_spectrum_data(self):
        # get spectrum data from the logic
        self._spectrometer_logic.take_spectrum_data()
        if self._mw.continuous_spectrum_acquisition_radioButton.isChecked():
            # if continuous acquisition is chosen, then call again the function get_spectrum_data
            self.sigContinueTakeSpectrum.emit()
        return

    def set_center_wavelength(self):
        # get center wavelength value from the gui
        center_wavelength = self._mw.set_wavelength_doubleSpinBox.value()
        # set new center wavelength value in the logic
        self._spectrometer_logic.set_center_wavelength(center_wavelength)
        # update wavelengths range in the gui
        self.update_spectrum_1d()
        return

    def set_grating(self):
        # get grating value from the gui
        grating = self._mw.grating_spinBox.value()
        # set new grating value in the logic
        self._spectrometer_logic.set_grating(grating)
        # update wavelengths range in the gui
        self.update_spectrum_1d()
        return
