import os
from core.module import Connector
from gui.guibase import GUIBase
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic


class MainWindow(QtWidgets.QMainWindow):
    """ The main window for the ODMR measurement GUI.
    """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'cavity_control_gui.ui')

        # Load it
        super(MainWindow, self).__init__()
        uic.loadUi(ui_file, self)
        self.show()


class CavityControlGui(GUIBase):
    """
    This is the GUI Class for WLT measurements
    """
    _modclass = 'WLTGui'
    _modtype = 'gui'

    # declare connectors
    acquisition_card_logic = Connector(interface='EmptyInterface')
    positioners_logic = Connector(interface='EmptyInterface')

    def on_activate(self):
        """ Definition, configuration and initialisation of the ODMR GUI.
        This init connects all the graphic modules, which were created in the
        *.ui file and configures the event handling between the modules.
        """
        # setting up main window
        self._mw = MainWindow()
        self._acquisition_card_logic = self.acquisition_card_logic()
        self._positioners_logic = self.positioners_logic()
        # configure all the modules of the GUI and connect the different hardwares
        self.config_positioner_control()
        self.config_pzt_scanner()
        # show window
        self._mw.show()

    def on_deactivate(self):
        """ Reverse steps of activation
        @return int: error code (0:OK, -1:error)
        """
        self._mw.close()
        return

    def config_pzt_scanner(self):
        self.scanner_moving = False
        # Ramp
        self._mw.scanner_ramp_frequency_DoubleSpinBox.setMaximum(10000)
        self._mw.scanner_ramp_frequency_DoubleSpinBox.setMinimum(0)
        self._mw.scanner_ramp_amplitude_DoubleSpinBox.setMinimum(0)
        self._mw.scanner_ramp_amplitude_DoubleSpinBox.setMaximum(20)
        self._mw.scanner_ramp_offset_DoubleSpinBox.setMinimum(-10)
        self._mw.scanner_ramp_offset_DoubleSpinBox.setMaximum(10)
        self._mw.scanner_ramp_amplitude_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        self._mw.scanner_ramp_frequency_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        self._mw.scanner_ramp_offset_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        # Sinewave
        self._mw.scanner_sinewave_frequency_DoubleSpinBox.setMaximum(10000)
        self._mw.scanner_sinewave_frequency_DoubleSpinBox.setMinimum(0)
        self._mw.scanner_sinewave_frequency_DoubleSpinBox.setMinimum(0)
        self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setMinimum(0)
        self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setMaximum(20)
        self._mw.scanner_sinewave_offset_DoubleSpinBox.setMinimum(-10)
        self._mw.scanner_sinewave_offset_DoubleSpinBox.setMaximum(10)
        self._mw.scanner_sinewave_amplitude_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        self._mw.scanner_sinewave_frequency_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        self._mw.scanner_sinewave_offset_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        # DC
        self._mw.scanner_dc_offset_DoubleSpinBox.setMinimum(-10)
        self._mw.scanner_dc_offset_DoubleSpinBox.setMaximum(10)
        self._mw.scanner_dc_offset_DoubleSpinBox.editingFinished.connect(self.scanner_value_edited)
        self._mw.scanner_start_PushButton.clicked.connect(self.start_scanner)
        self._mw.scanner_stop_PushButton.clicked.connect(self.stop_scanner)
        return

    def config_positioner_control(self):
        """Configuration of the gui module JPE_CPSHR3_control"""
        # disable the activation of moving JPE
        self._mw.lock_checkBox.setChecked(True)
        self._mw.step_xminus_pushButton.setEnabled(0)
        self._mw.step_yminus_pushButton.setEnabled(0)
        self._mw.step_zminus_pushButton.setEnabled(0)
        self._mw.step_xplus_pushButton.setEnabled(0)
        self._mw.step_yplus_pushButton.setEnabled(0)
        self._mw.step_zplus_pushButton.setEnabled(0)
        self._mw.cla1_step_up_pushButton.setEnabled(0)
        self._mw.cla1_step_down_pushButton.setEnabled(0)
        self._mw.cla2_step_up_pushButton.setEnabled(0)
        self._mw.cla2_step_down_pushButton.setEnabled(0)
        self._mw.cla3_step_up_pushButton.setEnabled(0)
        self._mw.cla3_step_down_pushButton.setEnabled(0)

        # get JPE parameters
        self._mw.jpe_frequency_spinBox.setValue(int(self._positioners_logic.get_frequency()))
        self._mw.jpe_step_size_spinBox.setValue(int(self._positioners_logic.get_step_size()))
        self._mw.jpe_temperature_spinBox.setValue(int(self._positioners_logic.get_temperature()))
        # get tracking value
        self._mw.x_tracking_doubleSpinBox.setValue(self._positioners_logic.open_positioners_tracking_file()[0])
        self._mw.y_tracking_doubleSpinBox.setValue(self._positioners_logic.open_positioners_tracking_file()[1])
        self._mw.z_tracking_doubleSpinBox.setValue(self._positioners_logic.open_positioners_tracking_file()[2])
        # connections
        self._mw.lock_checkBox.stateChanged.connect(self.lock_positioner)
        self._mw.step_xminus_pushButton.clicked.connect(self.move_x_negative)
        self._mw.step_xplus_pushButton.clicked.connect(self.move_x_positive)
        self._mw.step_yminus_pushButton.clicked.connect(self.move_y_negative)
        self._mw.step_yplus_pushButton.clicked.connect(self.move_y_positive)
        self._mw.step_zminus_pushButton.clicked.connect(self.move_z_negative)
        self._mw.step_zplus_pushButton.clicked.connect(self.move_z_positive)
        self._mw.cla1_step_up_pushButton.clicked.connect(self.move_positioner_1_up)
        self._mw.cla2_step_up_pushButton.clicked.connect(self.move_positioner_2_up)
        self._mw.cla3_step_up_pushButton.clicked.connect(self.move_positioner_3_up)
        self._mw.cla1_step_down_pushButton.clicked.connect(self.move_positioner_1_down)
        self._mw.cla2_step_down_pushButton.clicked.connect(self.move_positioner_2_down)
        self._mw.cla3_step_down_pushButton.clicked.connect(self.move_positioner_3_down)
        self._mw.stop_positionner_pushButton.clicked.connect(self.stop_motion)
        self._mw.jpe_temperature_spinBox.editingFinished.connect(self.set_positioner_temperature)
        self._mw.jpe_frequency_spinBox.editingFinished.connect(self.set_positioner_frequency)
        self._mw.jpe_step_size_spinBox.editingFinished.connect(self.set_positioner_step_size)
        self._positioners_logic.sigUpdateTrackingLogic.connect(self.update_positioner_tracking, QtCore.Qt.QueuedConnection)
        self._mw.reset_x_pushButton.clicked.connect(self._positioners_logic.reset_tracking_x)
        self._mw.reset_y_pushButton.clicked.connect(self._positioners_logic.reset_tracking_y)
        self._mw.reset_z_pushButton.clicked.connect(self._positioners_logic.reset_tracking_z)
        self._mw.set_x_pushButton.clicked.connect(self.set_x_tracking)
        self._mw.set_y_pushButton.clicked.connect(self.set_y_tracking)
        self._mw.set_z_pushButton.clicked.connect(self.set_z_tracking)

        self._positioners_logic.sigUpdateTrackingLogic.connect(self.update_positioner_tracking)

    def start_scanner(self):
        """ Start to move the fiber with the chosen driving signal"""
        # Get parameters from the window
        ramp_amplitude = self._mw.scanner_ramp_amplitude_DoubleSpinBox.value()
        ramp_freq = self._mw.scanner_ramp_frequency_DoubleSpinBox.value()
        ramp_offset = self._mw.scanner_ramp_offset_DoubleSpinBox.value()
        sinewave_amplitude = self._mw.scanner_sinewave_amplitude_DoubleSpinBox.value()
        sinewave_freq = self._mw.scanner_sinewave_frequency_DoubleSpinBox.value()
        sinewave_offset = self._mw.scanner_sinewave_offset_DoubleSpinBox.value()
        dc_offset = self._mw.scanner_dc_offset_DoubleSpinBox.value()
        if self._mw.scanner_ramp_radioButton.isChecked():
            # send ramp signal
            self._acquisition_card_logic.start_ramp(ramp_amplitude, ramp_freq, ramp_offset)
            self._mw.scanner_ramp_frequency_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_ramp_amplitude_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_ramp_offset_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_frequency_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_offset_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_dc_offset_DoubleSpinBox.setEnabled(False)
            self.scanner_moving = True
        elif self._mw.scanner_sinewave_radioButton.isChecked():
            # send sinewave
            self._acquisition_card_logic.start_sine_wave(sinewave_amplitude / 2, sinewave_freq, sinewave_offset)
            self._mw.scanner_ramp_frequency_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_ramp_amplitude_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_ramp_offset_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_frequency_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_offset_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_dc_offset_DoubleSpinBox.setEnabled(False)
            self.scanner_moving = True
        elif self._mw.scanner_dc_radioButton.isChecked():
            # send DC
            self._acquisition_card_logic.start_offset(dc_offset)
            self._mw.scanner_ramp_frequency_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_ramp_amplitude_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_ramp_offset_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_frequency_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_sinewave_offset_DoubleSpinBox.setEnabled(False)
            self._mw.scanner_dc_offset_DoubleSpinBox.setEnabled(True)
            self.scanner_moving = True
        elif self._mw.scanner_ramp_and_sine_radioButton.isChecked():
            # send ramp + sinewave
            self._acquisition_card_logic.start_ramp_sinewave(ramp_amplitude, ramp_freq, ramp_offset,
                                                    sinewave_amplitude, sinewave_freq, sinewave_offset)
            self._mw.scanner_ramp_frequency_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_ramp_amplitude_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_ramp_offset_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_frequency_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_sinewave_offset_DoubleSpinBox.setEnabled(True)
            self._mw.scanner_dc_offset_DoubleSpinBox.setEnabled(False)
            self.scanner_moving = True
        return

    def stop_scanner(self):
        """ Stop to move the fiber with the chosen driving signal"""
        self._acquisition_card_logic.stop_analog_output()
        self.scanner_moving = False
        # Enable changes to parameters
        self._mw.scanner_ramp_frequency_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_ramp_amplitude_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_ramp_offset_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_sinewave_frequency_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_sinewave_amplitude_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_sinewave_offset_DoubleSpinBox.setEnabled(True)
        self._mw.scanner_dc_offset_DoubleSpinBox.setEnabled(True)
        return

    def scanner_value_edited(self):
        """Modify signal sent to the scanner"""
        if self.scanner_moving:
            # The scanner is stopped and started again with the new parameters
            self.stop_scanner()
            self.start_scanner()
        else:
            pass
        return

    def lock_positioner(self):
        """Lock/unlock the GUI in order to not move the sample by mistake"""
        if self._mw.lock_checkBox.isChecked() == 0:
            # activate the control of the positioners
            self._mw.step_xminus_pushButton.setEnabled(1)
            self._mw.step_yminus_pushButton.setEnabled(1)
            self._mw.step_zminus_pushButton.setEnabled(1)
            self._mw.step_xplus_pushButton.setEnabled(1)
            self._mw.step_yplus_pushButton.setEnabled(1)
            self._mw.step_zplus_pushButton.setEnabled(1)
            self._mw.cla1_step_up_pushButton.setEnabled(1)
            self._mw.cla1_step_down_pushButton.setEnabled(1)
            self._mw.cla2_step_up_pushButton.setEnabled(1)
            self._mw.cla2_step_down_pushButton.setEnabled(1)
            self._mw.cla3_step_up_pushButton.setEnabled(1)
            self._mw.cla3_step_down_pushButton.setEnabled(1)
        else:
            # disable the control the positioners in order to avoid unwanted move of the sample
            self._mw.step_xminus_pushButton.setEnabled(0)
            self._mw.step_yminus_pushButton.setEnabled(0)
            self._mw.step_zminus_pushButton.setEnabled(0)
            self._mw.step_xplus_pushButton.setEnabled(0)
            self._mw.step_yplus_pushButton.setEnabled(0)
            self._mw.step_zplus_pushButton.setEnabled(0)
            self._mw.cla1_step_up_pushButton.setEnabled(0)
            self._mw.cla1_step_down_pushButton.setEnabled(0)
            self._mw.cla2_step_up_pushButton.setEnabled(0)
            self._mw.cla2_step_down_pushButton.setEnabled(0)
            self._mw.cla3_step_up_pushButton.setEnabled(0)
            self._mw.cla3_step_down_pushButton.setEnabled(0)
        return

    def move_positioner_1_up(self):
        """Move positioner_1 up by the displacement value"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_1(displacement)
        return

    def move_positioner_1_down(self):
        """Move positioner_1 down by the displacement value"""
        displacement = - self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_1(displacement)
        return

    def move_positioner_2_up(self):
        """Move positioner_2 up by the displacement value"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_2(displacement)
        return

    def move_positioner_2_down(self):
        """Move positioner_2 down by the displacement value"""
        displacement = - self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_2(displacement)
        return

    def move_positioner_3_up(self):
        """Move positioner_3 up by the displacement value"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_3(displacement)
        return

    def move_positioner_3_down(self):
        """Move positioner_3 down by the displacement value"""
        displacement = - self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_positioner_3(displacement)
        return

    def move_x_negative(self):
        """ Move sample toward negative x-values"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(- displacement, 0, 0)
        return

    def move_x_positive(self):
        """ Move sample toward positive x-values"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(displacement, 0, 0)
        return

    def move_y_negative(self):
        """ Move sample toward negative y-values"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(0, - displacement, 0)
        return

    def move_y_positive(self):
        """ Move sample toward positive y-values"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(0, displacement, 0)
        return

    def move_z_negative(self):
        """ Move sample toward negative z-values"""
        displacement = - self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(0, 0, displacement)
        return

    def move_z_positive(self):
        """ Move sample toward positive z-values"""
        displacement = self._mw.displacement_doubleSpinBox.value() * 1e-6
        self._positioners_logic.move_xyz(0, 0, displacement)
        return

    def stop_motion(self):
        """Send the command to the controller to stop CLAs"""
        self._positioners_logic.stop_positioner()
        return

    def set_positioner_temperature(self):
        """ Set JPE temperature"""
        temperature = self._mw.jpe_temperature_spinBox.value()
        self._positioners_logic.set_temperature(temperature)
        return

    def set_positioner_frequency(self):
        """ Set JPE frequency"""
        frequency = self._mw.jpe_frequency_spinBox.value()
        self._positioners_logic.set_frequency(frequency)
        return

    def set_positioner_step_size(self):
        """ Set JPE amplitude step size"""
        step_size = self._mw.jpe_step_size_spinBox.value()
        self._positioners_logic.set_step_size(step_size)
        return

    def set_x_tracking(self):
        """Set manually the value of X tracking"""
        x_tracking = self._mw.x_tracking_doubleSpinBox.value()
        self._positioners_logic.set_x_tracking(x_tracking)

    def set_y_tracking(self):
        """Set manually the value of Y tracking"""
        y_tracking = self._mw.y_tracking_doubleSpinBox.value()
        self._positioners_logic.set_y_tracking(y_tracking)

    def set_z_tracking(self):
        """Set manually the value of Z tracking"""
        z_tracking = self._mw.z_tracking_doubleSpinBox.value()
        self._positioners_logic.set_z_tracking(z_tracking)

    def update_positioner_tracking(self):
        """Update on the GUI the tracking position of the sample"""
        x_tracking = self._positioners_logic.get_x_tracking() * 1e6
        y_tracking = self._positioners_logic.get_y_tracking() * 1e6
        z_tracking = self._positioners_logic.get_z_tracking() * 1e6
        self._mw.x_tracking_doubleSpinBox.setValue(x_tracking)
        self._mw.y_tracking_doubleSpinBox.setValue(y_tracking)
        self._mw.z_tracking_doubleSpinBox.setValue(z_tracking)
        return
