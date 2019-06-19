# -*- coding: utf-8 -*-
"""
This file contains the Qudi Hardware module CPSRH3 class.

JPE : Jansen Precision Engeneering
CPSHR : Cryo Positionning Stage High Resonnance
CLA : Cryogenic Linear Actuator

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
import subprocess
import os
from core.module import Base
from interface.empty_interface import EmptyInterface
import numpy as np
from qtpy import QtCore


class JpeCpshr3Hardware(Base, EmptyInterface):
    """ CPSHR3_hardware class """

    _modtype = 'JpeCpshr3Hardware'
    _modclass = 'hardware'

    sigUpdateTracking = QtCore.Signal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # cacli.exe absolute path
        # download on https://www.janssenprecisionengineering.com/page/cryo-positioning-systems-controller/
        path = r"C:\Users\olgob\Desktop\qudi_diamond_lab"
        filename = "cacli.exe"
        self.cacli_path = os.path.join(path, filename)
        # Create 3 CLA objects corresponding to the 3 CLA of the hardware
        self.cla1 = CLA(1, 1, 'CA1801', 293, 0, 600, 100, 25e-9, 0)
        self.cla2 = CLA(2, 1, 'CA1801', 293, 0, 600, 100, 25e-9, 0)
        self.cla3 = CLA(3, 1, 'CA1801', 293, 0, 600, 100, 25e-9, 0)
        # Fixed CPSHR3 parameters determined by the geometry of the hardware
        self.cla_radius = 26e-3  # unit : meter
        self.sample_height = 55e-3  # unit : meter
        self.cla1_displacement = 0  # CLA1 displacement value
        self.cla2_displacement = 0  # CLA2 displacement value
        self.cla3_displacement = 0  # CLA3 displacement value
        self.x_tracking, self.y_tracking, self.z_tracking = 0, 0, 0  # tracking value

    def on_activate(self):
        """ Initialisation performed during activation of the module."""
        # No command required to have the positioner ready
        pass

    def on_deactivate(self):
        """ Shut down hardware """
        # No command required
        pass

    def reset_hardware(self):
        """ Reset Hardware """
        # No command required
        pass

    def do_command(self, cmd_line):
        """Open the cacli.exe file provided by JPE and execute a command line like specified in the software manual
        available on JPE website"""
        # print(cmd_line)
        proc = subprocess.Popen(self.cacli_path + ' ' + cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.stdout.read().decode('utf-8').strip()  # .split()
        return output

    def get_cla_status(self, cla_number):
        """ Get the status of a CLA : Moving (return True) or Stopped (return False) """
        status = self.do_command('STS ' + str(cla_number))
        if status == 'STATUS : STOP\r\nFAILSAFE STATE: 0x0':
            return False
        elif status == 'STATUS : MOVE':
            return True

    def cla_displacement(self, delta_x, delta_y, delta_z):
        """ Calculate the displacement of each CLA in function of the displacement wanted using transfer matrix"""
        input_vector = np.matrix([delta_x, delta_y, delta_z])
        transfer_matrix = np.matrix([
            [-(self.cla_radius * np.sqrt(3)) / (2 * self.sample_height), self.cla_radius / (2 * self.sample_height), 1],
            [0, -self.cla_radius / self.sample_height, 1],
            [(self.cla_radius * np.sqrt(3)) / (2 * self.sample_height), self.cla_radius / (2 * self.sample_height), 1]
        ])
        output_vector = transfer_matrix * input_vector.T
        return output_vector[0, 0], output_vector[1, 0], output_vector[2, 0]

    def get_xyz_displacement(self, delta_z1, delta_z2, delta_z3):
        """ Calculate the displacement on the sample in function of the displacement of each CLA using transfer
        matrix """
        input_vector = np.matrix([delta_z1, delta_z2, delta_z3])
        transfer_matrix = 1 / (3 * self.cla_radius) * np.matrix([
             [-self.sample_height * np.sqrt(3), 0, self.sample_height * np.sqrt(3)],
             [self.sample_height, -2 * self.sample_height, self.sample_height],
             [self.cla_radius, self.cla_radius, self.cla_radius]
             ])
        output_vector = np.dot(transfer_matrix, input_vector.getT())
        return output_vector[0, 0], output_vector[1, 0], output_vector[2, 0]

    def get_steps_number(self, displacement):
        """ Get the closest integer number of steps for a specified CLA displacement """
        step_amp = self.cla1.get_step_amp_max()
        number_of_steps = np.abs(np.rint(displacement / step_amp))
        return number_of_steps

    def stop_positioner(self):
        """ Send the command to the controller to stop the CLAs
        (Does not work if the program is executing function in another thread) """
        self.do_command('STP 1')
        self.do_command('STP 2')
        self.do_command('STP 3')
        return

    def get_cli_ver(self):
        """ Get CLI version information """
        self.do_command('/ver')
        return

    def get_list_cla_type(self):
        """ List supported cryo linear actuator (CLA) types """
        self.do_command('/type')
        return

    def get_module_info(self):
        """ Get information about installed modules"""
        self.do_command('modlist')
        return

    def get_actuators_info(self):
        """ Get information on actuator types set """
        command = 'INFO 1 1'
        self.do_command(command)
        command = 'INFO 1 2'
        self.do_command(command)
        command = 'INFO 1 3'
        self.do_command(command)
        return

    def get_module_description(self):
        """ Get information on installed modules """
        command = 'DESC 1'
        self.do_command(command)
        return

    def edit_cmd_line(self, *list_parameters):
        """ Convert a list of parameters into a command line suitable for cacli.exe software """
        cmd_line = str(' '.join(list_parameters))
        return cmd_line

    def cla1_displacement_cmd_line(self, displacement):
        """ Set the parameters on a CLA 1 to a desired displacement """
        # Set the CLA steps number to the closer integer corresponding to the desired displacement
        self.cla1.set_steps(self.get_steps_number(displacement))
        # Determination of the rotation clockwise (1) or counter-clockwise (0) of the CLA
        if displacement < 0:
            self.cla1.set_dir(1)
        elif displacement > 0:
            self.cla1.set_dir(0)
        # Creation of the command line for the CLA
        cla1_cmd_line = 'MOV ' + self.edit_cmd_line(self.cla1.get_addr(),
                                                    self.cla1.get_ch(),
                                                    self.cla1.get_type(),
                                                    self.cla1.get_temp(),
                                                    self.cla1.get_dir(),
                                                    self.cla1.get_freq(),
                                                    self.cla1.get_rel(),
                                                    self.cla1.get_steps())
        return cla1_cmd_line

    def cla2_displacement_cmd_line(self, displacement):
        """ Set the parameters on a CLA 2 to a desired displacement """
        # Set the CLA steps number to the closer integer corresponding to the desired displacement
        self.cla2.set_steps(self.get_steps_number(displacement))
        # Determination of the rotation clockwise (1) or counter-clockwise (0) of the CLA
        if displacement < 0:
            self.cla2.set_dir(1)
        elif displacement > 0:
            self.cla2.set_dir(0)
        # Creation of the command line for the CLA
        cla2_cmd_line = 'MOV ' + self.edit_cmd_line(self.cla2.get_addr(),
                                                    self.cla2.get_ch(),
                                                    self.cla2.get_type(),
                                                    self.cla2.get_temp(),
                                                    self.cla2.get_dir(),
                                                    self.cla2.get_freq(),
                                                    self.cla2.get_rel(),
                                                    self.cla2.get_steps())
        return cla2_cmd_line

    def cla3_displacement_cmd_line(self, displacement):
        """ Set the parameters on a CLA 3 to a desired displacement """
        # Set the CLA steps number to the closer integer corresponding to the desired displacement
        self.cla3.set_steps(self.get_steps_number(displacement))
        # Determination of the rotation clockwise (1) or counter-clockwise (0) of the CLA
        if displacement < 0:
            self.cla3.set_dir(1)
        elif displacement > 0:
            self.cla3.set_dir(0)
        # Creation of the command line for the CLA
        cla3_cmd_line = 'MOV ' + self.edit_cmd_line(self.cla3.get_addr(),
                                                    self.cla3.get_ch(),
                                                    self.cla3.get_type(),
                                                    self.cla3.get_temp(),
                                                    self.cla3.get_dir(),
                                                    self.cla3.get_freq(),
                                                    self.cla3.get_rel(),
                                                    self.cla3.get_steps())
        return cla3_cmd_line

    def move_xyz(self, delta_x, delta_y, delta_z):
        """ Move the sample using xyz coordinate system relative to the actual position of the sample """
        # calculation of the CLAs displacement
        self.cla1_displacement, self.cla2_displacement, self.cla3_displacement = self.cla_displacement(delta_x, delta_y,
                                                                                                       delta_z)
        # execute the command lines for each CLA
        self.move_positioner_1(self.cla1_displacement)
        self.move_positioner_2(self.cla2_displacement)
        self.move_positioner_3(self.cla3_displacement)
        return

    def move_positioner_1(self, displacement):
        """ Move the CLA 1 """
        cla1_displacement_cmd_line = self.cla1_displacement_cmd_line(displacement)
        # IF A COMMAND IS SEND TO THE CONTROLLER WITH STEPS NUMBER = 0,
        # IT IS EQUIVALENT TO INFINITE MOTION FOR CALCLII SOFTWARE !
        if self.cla1.get_steps() != '0':
            # send the command to the controller
            self.do_command(cla1_displacement_cmd_line)
            # update the tracking of the position of the sample
            self.update_tracking(displacement, 0, 0)
        return

    def move_positioner_2(self, displacement):
        """ Move the CLA 2 """
        cla2_cmd_line = self.cla2_displacement_cmd_line(displacement)
        # IF A COMMAND IS SEND TO THE CONTROLLER WITH STEPS NUMBER = 0,
        # IT IS EQUIVALENT TO INFINITE MOTION FOR CALCLII SOFTWARE !
        if self.cla2.get_steps() != '0':
            # send the command to the controller
            self.do_command(cla2_cmd_line)
            # update the tracking of the position of the sample
            self.update_tracking(0, displacement, 0)
            return

    def move_positioner_3(self, displacement):
        """ Move the CLA 3 """
        cla3_cmd_line = self.cla3_displacement_cmd_line(displacement)
        # IF A COMMAND IS SEND TO THE CONTROLLER WITH STEPS NUMBER = 0,
        # IT IS EQUIVALENT TO INFINITE MOTION FOR CALCLII SOFTWARE !
        if self.cla3.get_steps() != '0':
            # Send the command to the controller
            self.do_command(cla3_cmd_line)
            # update the tracking of the position of the sample
            self.update_tracking(0, 0, displacement)
        return

    def set_temperature(self, temperature):
        """ Set the temperature parameter of the CLAs """
        self.cla1.set_temp(temperature)
        self.cla2.set_temp(temperature)
        self.cla3.set_temp(temperature)
        return

    def get_temperature(self):
        """ Get the temperature parameter of the CLAs """
        return self.cla1.get_temp()

    def get_frequency(self):
        """ Get the CLAs frequency """
        return self.cla1.get_freq()

    def set_frequency(self, frequency):
        """ Set the CLAs frequency """
        self.cla1.set_freq(frequency)
        self.cla2.set_freq(frequency)
        self.cla3.set_freq(frequency)
        return

    def get_step_size(self):
        """ Get the CLAs relative step size
        @293K : 100% = 25 nm, step size 5-25 nm
        @4K : 100% = 5nm, step size 1-5 nm """
        return self.cla1.get_rel()

    def set_step_size(self, step_size):
        """ Set the CLAs relative step size
        @293K : 100% = 25 nm, step size 5-25 nm
        @4K : 100% = 5nm, step size 1-5 nm """
        self.cla1.set_rel(step_size)
        self.cla2.set_rel(step_size)
        self.cla3.set_rel(step_size)
        return

    def set_x_tracking(self, x_tracking):
        """ Set X tracking value """
        self.x_tracking = x_tracking

    def get_x_tracking(self):
        """ Get X tracking value """
        return self.x_tracking

    def set_y_tracking(self, y_tracking):
        """ Set Y tracking value """
        self.y_tracking = y_tracking

    def get_y_tracking(self):
        """ Get Y tracking value """
        return self.y_tracking

    def set_z_tracking(self, z_tracking):
        """ Set Z tracking value """
        self.z_tracking = z_tracking

    def get_z_tracking(self):
        """ Get Z tracking value """
        return self.z_tracking

    def update_tracking(self, cla1_displacement, cla2_displacement, cla3_displacement):
        """ Calculate the actual displacement of the sample taking into account the fact that the positioners can only
        move by fixed steps size """
        # Get the number of steps realized for each CLA
        cla1_displacement = self.get_steps_number(cla1_displacement) * self.cla1.get_step_amp_max() * np.sign(
            cla1_displacement)
        cla2_displacement = self.get_steps_number(cla2_displacement) * self.cla1.get_step_amp_max() * np.sign(
            cla2_displacement)
        cla3_displacement = self.get_steps_number(cla3_displacement) * self.cla1.get_step_amp_max() * np.sign(
            cla3_displacement)
        # Get the sample displacement
        x_tracking, y_tracking, z_tracking = self.get_xyz_displacement(cla1_displacement, cla2_displacement,
                                                                       cla3_displacement)
        # update the value of tracking
        self.set_x_tracking(x_tracking)
        self.set_y_tracking(y_tracking)
        self.set_z_tracking(z_tracking)
        # emit signal to updtae the tracking values in the logic
        self.sigUpdateTracking.emit()
        return


class CLA:
    """ Cryogenic Linear Actuator class """

    def __init__(self, cla_addr, cla_ch, cla_type, cla_temp, cla_dir, cla_freq, cla_rel, cla_step_amp_max, cla_steps):
        """ Initialization of a CLA """
        self.cla_addr = str(cla_addr)  # Adress of the module corresponding to the CLA
        self.cla_ch = str(cla_ch)  # Channel on the module corresponding to the CLA
        self.cla_type = str(cla_type)  # CLA type (CA1801)
        self.cla_temp = str(cla_temp)  # Temperature (unit : Kelvin)
        self.cla_dir = str(cla_dir)  # CLA direction (1 : clockwise, 0 : counter-clockwise)
        self.cla_freq = str(cla_freq)  # Frequency of operation (unit : Hz)
        self.cla_rel = str(cla_rel)  # (Relative) Piezo step size (unit : %)
        self.cla_step_amp_max = cla_step_amp_max  # Maximum Piezo step size (unit : meter)
        self.cla_steps = str(cla_steps)  # Number of actuation steps

    def set_addr(self, addr):
        """ Set the adress of the module corresponding to the CLA """
        self.cla_addr = str(addr)

    def get_addr(self):
        """ Get the adress of the module corresponding to the CLA """
        return self.cla_addr

    def set_ch(self, ch):
        """ Set the channel on the module corresponding to the CLA """
        self.cla_ch = str(ch)

    def get_ch(self):
        """Get the channel on the module corresponding to the CLA """
        return self.cla_ch

    def set_type(self, cla_type):
        """ Set the CLA type """
        self.cla_type = cla_type

    def get_type(self):
        """ Get the CLA type """
        return self.cla_type

    def set_temp(self, temp):
        """ Set the operation temperature of the CLA """
        self.cla_temp = str(temp)

    def get_temp(self):
        """ Get the operation temperature of the CLA (entered by the user, not measured!) """
        return self.cla_temp

    def set_dir(self, direction):
        """ Set the CLA direction (1 : clockwise, 0 : counter-clockwise) """
        self.cla_dir = str(direction)

    def get_dir(self):
        """ Get the CLA direction (1 : clockwise, 0 : counter-clockwise) """
        return self.cla_dir

    def set_freq(self, freq):
        """ Set the CLA frequency of operation (unit : Hz) from 0 to 600 Hz """
        self.cla_freq = str(freq)

    def get_freq(self):
        """ Get the CLA frequency of operation (unit : Hz) from 0 to 600 Hz """
        return self.cla_freq

    def set_rel(self, rel):
        """ Set (Relative) Piezo step size (unit : %) """
        self.cla_rel = str(rel)

    def get_rel(self):
        """ Get (Relative) Piezo step size (unit : %) """
        return self.cla_rel

    def set_step_amp_max(self, step_amp_max):
        """ Set maximum Piezo step size (unit : meter) specified 5-25nm by JPE """
        self.cla_step_amp_max = step_amp_max

    def get_step_amp_max(self):
        """ Get maximum Piezo step size (unit : meter) (specified by user, not measured!) """
        return self.cla_step_amp_max

    def set_steps(self, steps):
        """ Set the number of actuation steps """
        self.cla_steps = str(steps)

    def get_steps(self):
        """ Get the number of actuation steps (specified by user, not measured!) """
        return self.cla_steps
