from qtpy import QtCore
from logic.generic_logic import GenericLogic
from core.module import Connector
import numpy as np
import time

class SpectrometerLogic(GenericLogic):
    """
    This is the Logic class for cavity white light transmission measurement.
    """
    _modclass = 'SpectrometerLogic'
    _modtype = 'logic'

    # declare connectors
    andor_cam = Connector(interface='SpectrometerInterface')
    shamrock_spectrometer = Connector(interface='SpectrometerInterface')
    # savelogic = Connector(interface='SaveLogic')

    # Qt signals
    sigSpectrum1DUpdate = QtCore.Signal()
    sigSpectrum2DUpdate = QtCore.Signal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_data = np.zeros(1024)
        self.spectrum_data = np.zeros(1024)
        self.background_subtracted = False
        self.wavelengths_array = np.linspace(400, 800, 1024)

    def on_activate(self):
        """ Initialisation performed during activation of the module"""
        self._andor_cam = self.andor_cam()
        self._shamrock_spectrometer = self.shamrock_spectrometer()

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._andor_cam.on_deactivate()
        self._shamrock_spectrometer.on_desactivate()
        return

    def set_camera_temperature(self, temperature):
        """ Sets the temperature for the spectrometer in Celsius [-75, 25] """
        self._andor_cam.set_temperature(temperature)
        return

    def get_camera_temperature(self):
        """ Gets the temperature for the camera in spectrometer """
        return self._andor_cam.get_temperature()

    def set_camera_cycle_time(self, cycle_time):
        """ Set the cycle time of the camera """
        self._andor_cam.set_cycle_time(cycle_time)
        return

    def get_camera_cycle_time(self):
        """ Get the cycle time of the camera """
        return self._andor_cam.get_cycle_time()

    def set_camera_exposure_time(self, exposure_time):
        """ Set the exposure time for the camera """
        self._andor_cam.set_exposure_time(exposure_time)
        return

    def get_camera_exposure_time(self):
        """ Get the exposure time for the camera """
        return self._andor_cam.get_exposure_time()

    def set_camera_number_accumulations(self, number_accumulations):
        """ Set the number of accumulations of the spectrometer (int) """
        self._andor_cam.set_number_accumulations(number_accumulations)
        return

    def get_camera_number_accumulations(self):
        """ Get the number of accumulations of the spectrometer (int) """
        return self._andor_cam.get_number_accumulations()

    def set_camera_cooler_on(self):
        """ Activate the cool down of the spectrometer camera """
        self._andor_cam.cooler_on()
        return

    def set_camera_cooler_off(self):
        """ Desactivate the cool down of the spectrometer camera """
        self._andor_cam.cooler_off()
        return

    def get_camera_size(self):
        """ Get the dimension (width, height) of the camera """
        return self._andor_cam.get_camera_size()

    def get_spectrum_data(self):
        """ Get spectrum data """
        return self.spectrum_data

    def take_spectrum_data(self):
        """ Acquire spectrum tacking background subtraction into account"""
        self.spectrum_data = self._andor_cam.take_spectrum() - self.get_background_data()
        self.sigSpectrum1DUpdate.emit()
        return self.spectrum_data

    def set_background_data(self):
        """ Set background spectrum """
        self.background_data = self._andor_cam.take_spectrum()
        return

    def get_background_data(self):
        """ Get background spectrum """
        return self.background_data

    def reset_background_data(self):
        """ Reset background spectrum """
        self.background_data = np.zeros(1024)
        return

    def set_center_wavelength(self, center_wavelength):
        """ Set the center wavelength of the spectrometer rotating the grating"""
        self._shamrock_spectrometer.set_center_wavelength(center_wavelength)
        self.set_wavelengths_array()

    def get_center_wavelength(self):
        """ Get the center wavelength of the spectrometer """
        return self._shamrock_spectrometer.get_center_wavelength()

    def get_grating(self):
        """ Get the grating of the spectrometer
        0: 150 lines / mm
        1: 300 lines / mm
        2: 1200 lines / mm """
        return self._shamrock_spectrometer.get_grating()

    def set_grating(self, grating):
        """ Set the grating of the spectrometer
        0: 150 lines / mm
        1: 300 lines / mm
        2: 1200 lines / mm """
        self._shamrock_spectrometer.set_grating(grating)
        self.set_wavelengths_array()
        return

    def get_wavelength_range(self):
        """ Get the wavelength range visible on the camera """
        return self._shamrock_spectrometer.get_wavelength_range()

    def get_wavelengths(self):
        wavelength_min, wavelength_max = self.get_wavelength_range()
        wavelengths_array_size = self.get_camera_size()[0]
        wavelengths = np.linspace(wavelength_min, wavelength_max, wavelengths_array_size)
        return wavelengths

    def save_spectrum_data(self):
        """Save the data of the acquired spectrum"""
        local_time = time.localtime()
        filename = str(local_time[0]) + '_' + str(local_time[1]) + '_' + str(local_time[2]) + '_' + str(
            local_time[3]) + '_' + str(local_time[4]) + '_' + str(local_time[5]) + '_spectrum_data.txt'
        data = [self.get_wavelengths(), self.get_spectrum_data()]
        np.savetxt(filename, data, delimiter=',')
        return

    def set_wavelengths_array(self):
        wavelength_min, wavelength_max = self.get_wavelength_range()
        wavelength_array_size = self.get_camera_size()[0]
        self.wavelengths_array = np.linspace(wavelength_min, wavelength_max, wavelength_array_size)
        return
