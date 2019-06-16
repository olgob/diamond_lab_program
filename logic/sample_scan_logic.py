from qtpy import QtCore
import numpy as np
from logic.generic_logic import GenericLogic
from core.module import Connector
import time


class SampleScanLogic(GenericLogic):
    """
    This is the Logic class for the scanning of the cavity (2D and 3D).
    """
    _modclass = 'SampleScanLogic'
    _modtype = 'logic'

    # declare connectors
    counter = Connector(interface='EmptyInterface')
    positioner_logic = Connector(interface='EmptyInterface')

    # signals
    sigUpdateAPDsImages = QtCore.Signal()

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.integration_time = 1
        self.xy_range = 10
        self.xy_step = 1
        self.positioners_steps_full_fsr = 1
        self.scan_steps_full_fsr = 1
        self.point = 0
        self.line = 0
        self.scan_iteration = 0
        self.apd1_data = np.zeros([int(self.xy_range / self.xy_step) + 1, int(self.xy_range / self.xy_step) + 1])
        self.apd2_data = np.zeros([int(self.xy_range / self.xy_step) + 1, int(self.xy_range / self.xy_step) + 1])
        self.apd1_matrix = np.empty([int(self.get_xy_range() / self.get_xy_step() + 1),
                                     int(self.get_xy_range() / self.get_xy_step() + 1),
                                     100], dtype=int)
        self.apd2_matrix = np.empty([int(self.get_xy_range() / self.get_xy_step() + 1),
                                     int(self.get_xy_range() / self.get_xy_step() + 1),
                                     100], dtype=int)

    def on_activate(self):
        """ Initialisation performed during activation of the module """
        # QUDI connectors (can only be declared in on_activate function)
        self._counter = self.counter()
        self._positioner_logic = self.positioner_logic()
        # connections

        # signals

    def on_deactivate(self):
        """ Reverse steps of activation """
        self._counter.on_deactivate()

    def set_integration_time(self, integration_time):
        """ Set integration time (s) of the APDs """
        self.integration_time = integration_time

    def get_integration_time(self):
        """ Get integration time (s) of the APDs """
        return self.integration_time

    def set_xy_range(self, xy_range):
        """ Set xy range (um) of the scan """
        self.xy_range = xy_range

    def get_xy_range(self):
        """ Get xy range (um) of the scan """
        return self.xy_range

    def set_xy_step(self, xy_step):
        """ Set xy step size (um) of the scan """
        self.xy_step = xy_step

    def get_xy_step(self):
        """ Get xy step size (um) of the scan """
        return self.xy_step

    def set_positioners_steps_full_fsr(self, positioners_steps_full_fsr):
        """ Set the necessary positioner steps number to access a full FSR of the cavity """
        self.positioners_steps_full_fsr = positioners_steps_full_fsr

    def get_positioners_steps_full_fsr(self):
        """ Get the necessary positioner steps number to access a full FSR of the cavity """
        return self.positioners_steps_full_fsr

    def set_apd1_data(self, xy_range, xy_step):
        """ Set APD1 data 2D array shape for a (xy_range, xy_step) value"""
        self.apd1_data = np.zeros([int(xy_range / xy_step) + 1, int(xy_range / xy_step) + 1])

    def get_apd1_data(self):
        """ Get APD1 data 2D array"""
        return self.apd1_data

    def set_apd2_data(self, xy_range, xy_step):
        """ Set APD2 data 2D array shape for a (xy_range, xy_step) value"""
        self.apd2_data = np.zeros([int(xy_range / xy_step) + 1, int(xy_range / xy_step) + 1])

    def get_apd2_data(self):
        """ Get APD1 data 2D array"""
        return self.apd2_data

    def set_point(self, point):
        """ Set the point number value that is scanned on a line """
        self.point = point

    def get_point(self):
        """ Get the point number value that is scanned on a line """
        return self.point

    def set_line(self, line):
        """ Set the line number value on the snake scan """
        self.line = line

    def get_line(self):
        """ Get the line number value on the snake scan """
        return self.line

    def set_scan_iteration(self, scan_iteration):
        """ Set the iteration number value on the snake scan """
        self.scan_iteration = scan_iteration

    def get_scan_iteration(self):
        """ Get the iteration number value on the snake scan """
        return self.scan_iteration

    def initialize_snake_scan(self, xy_range, xy_step, integration_time):
        """Initialize the snake scan taking the parameters from the gui
        xy_range : range of the scan (um)
        xy_step : step size (um)
        apd_integration_time : integration time of acquisition on each point (s)
        positioners_steps : step necessary to the device to scan one full FSR of the cavity
        apd_integration_time: integration time of acquisition on each point(s) """
        self.initialize_counter_scan()
        self.set_integration_time(integration_time)
        self.set_xy_step(xy_step)
        self.set_xy_range(xy_range)
        self.set_point(0)
        self.set_line(0)
        self.set_scan_iteration(0)
        clock_frequency = self._counter.get_clock_frequency()
        # initialize APDs data matrices that will keep all counts on each XY position
        self.apd1_matrix = np.empty([int(xy_range / xy_step + 1),
                                     int(xy_range / xy_step + 1),
                                     int(clock_frequency * integration_time)], dtype=int)
        self.apd2_matrix = np.empty([int(xy_range / xy_step + 1),
                                     int(xy_range / xy_step + 1),
                                     int(clock_frequency * integration_time)], dtype=int)
        self.set_apd1_data(xy_range, xy_step)
        self.set_apd2_data(xy_range, xy_step)
        # update APD images on the gui
        self.sigUpdateAPDsImages.emit()
        return

    def continue_snake_scan(self):
        """ Scan a square area around a central spot describing a snake movement """
        # get the necessary variables values for the acquisition
        xy_range = self.get_xy_range()
        xy_step = self.get_xy_step()
        line = self.get_line()
        point = self.get_point()
        scan_iteration = self.get_scan_iteration()
        if scan_iteration == 0:
            # first snake scan iteration : moving to origin of the scan (bottom left corner)
            self._positioner_logic.move_xyz(-(xy_range / 2) * 1e-6, -(xy_range / 2) * 1e-6, 0)
            # get counts
            apd1_counts, apd2_counts = self.get_counts()
            # save all counts into APDs matrices
            self.apd1_matrix[line, point] = apd1_counts
            self.apd2_matrix[line, point] = apd2_counts
            # save the average value of the counts in the 2D APDs data (that will be shown on the gui)
            self.apd1_data[line, point] = np.average(apd1_counts)
            self.apd2_data[line, point] = np.average(apd2_counts)
            # increment the point and the scan iteration by 1
            self.point += 1
            self.scan_iteration += 1
            # send signal to gui to update the APDs data
            self.sigUpdateAPDsImages.emit()
            return
        elif scan_iteration == int((xy_range / xy_step + 1) ** 2):
            # last snake scan iteration after the last point is scanned
            if line % 2 == 0:
                # the last point is on the upper left corner, so we move right down to the center
                self._positioner_logic.move_xyz(-(xy_range / 2) * 1e-6, -(xy_range / 2) * 1e-6, 0)
            else:
                # the last point is on the upper right corner, so we move left down to the center
                self._positioner_logic.move_xyz((xy_range / 2) * 1e-6, -(xy_range / 2) * 1e-6, 0)
            # increment of scan_iteration by 1
            self.scan_iteration += 1
            # close the counter and the clock of the counter
            self.close_counter_scan()
            return
        elif scan_iteration > int((xy_range / xy_step + 1) ** 2):
            # scan iteration is over the maximum of scan iterations required for (xy_range, xy_step) configuration
            return
        else:
            # other snake scan iterations
            if point == int(xy_range / xy_step + 1):
                # line completed : line is incremented by 1 and point is rebooted to 0
                self.line += 1
                line = self.get_line()
                self.set_point(0)
                point = self.get_point()
                # the sample is moved up
                self._positioner_logic.move_xyz(0, xy_step * 1e-6, 0)
                # get counts
                apd1_counts, apd2_counts = self.get_counts()
                if self.get_line() % 2 == 0:
                    # if the scan goes from left to right on the line
                    self.apd1_matrix[line, point] = apd1_counts
                    self.apd2_matrix[line, point] = apd2_counts
                    # we save the counts from left to right inside the APDs 2D and 3D data
                    self.apd1_data[line, point] = np.average(apd1_counts)
                    self.apd2_data[line, point] = np.average(apd2_counts)
                else:
                    # if the scan goes from right to left on the line
                    self.apd1_matrix[line, point] = apd1_counts
                    self.apd2_matrix[line, point] = apd2_counts
                    # we save the counts from right to left inside the APDs 2D and 3D data
                    self.apd1_data[line, np.size(self.apd1_data, 0) - point % np.size(self.apd1_data, 0) - 1] = np.average(apd1_counts)
                    self.apd2_data[line, np.size(self.apd1_data, 0) - point % np.size(self.apd1_data, 0) - 1] = np.average(apd2_counts)
            else:
                # Line not completed
                if line % 2 == 0:
                    # Horizontal move (positive way)
                    self._positioner_logic.move_xyz(xy_step * 1e-6, 0, 0)
                    # print('moving right', '(' + str(self.xy_step * 1e-6) + ', 0' + ', ' + '0)')
                    apd1_counts, apd2_counts = self.get_counts()
                    self.apd1_matrix[line, point] = apd1_counts
                    self.apd2_matrix[line, point] = apd2_counts
                    self.apd1_data[line, point] = np.average(apd1_counts)
                    self.apd2_data[line, point] = np.average(apd2_counts)
                else:
                    # Horizontal move (negative way)
                    self._positioner_logic.move_xyz(-xy_step * 1e-6, 0, 0)
                    # print('moving left', '(' + str(-self.xy_step * 1e-6) + ', 0' + ', ' + '0)')
                    apd1_counts, apd2_counts = self.get_counts()
                    self.apd1_matrix[line, point] = apd1_counts
                    self.apd2_matrix[line, point] = apd2_counts
                    self.apd1_data[line, np.size(self.apd1_data, 0) - point % np.size(self.apd1_data, 0) - 1] = np.average(apd1_counts)
                    self.apd2_data[line, np.size(self.apd1_data, 0) - point % np.size(self.apd1_data, 0) - 1] = np.average(apd2_counts)
            # increment the point and the scan iteration by 1
            self.point += 1
            self.scan_iteration += 1
            # send signal to gui to update the APDs data
            self.sigUpdateAPDsImages.emit()
            return

    def get_counts(self):
        """ Get counts from the counter """
        clock_frequency = self._counter.get_clock_frequency()
        integration_time = self.get_integration_time()
        samples = clock_frequency * integration_time
        counts = self._counter.get_counter(samples)
        apd1_counts = counts[0]
        apd2_counts = counts[1]
        return apd1_counts, apd2_counts

    def save_snake_scan_data(self):
        """ Save the data of the 2 APD pictures visible on the GUI """
        local_time = time.localtime()
        filename_apd1 = str(local_time[0]) + '_' + str(local_time[1]) + '_' + str(local_time[2]) + '_' + str(
            local_time[3]) + '_' + str(local_time[4]) + '_' + str(local_time[5]) + 'apd1_snake_scan_data.txt'
        filename_apd2 = str(local_time[0]) + '_' + str(local_time[1]) + '_' + str(local_time[2]) + '_' + str(
            local_time[3]) + '_' + str(local_time[4]) + '_' + str(local_time[5]) + 'apd2_snake_scan_data.txt'
        np.savetxt(filename_apd1, self.apd1_data, delimiter=',')
        np.savetxt(filename_apd2, self.apd2_data, delimiter=',')
        return

    def close_counter_scan(self):
        """ Close the counter and the clock of the counter """
        self._counter.close_counter()
        self._counter.close_clock()
        return

    def initialize_counter_scan(self):
        """ Configure the counters channels of the 2 APDs for a 2D or 3D scan """
        self._counter.set_up_clock()
        self._counter.set_up_counter()
        return
