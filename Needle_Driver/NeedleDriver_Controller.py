import time
import threading
import serial
import re

class NeedleDriverController():
    def __init__(self):
        """Initialise with the following parameters. Change here if necessary

        """
        #-------- Values for needle driver connection settings"
        self.port = "COM3"
        self.baudrate = 9600
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.timeout = 0.1  # Specify the timeout value in seconds

        #-------Float values of X, Y, Z readings
        """Float values of current position of x, y, z values initialised to 0.00
        """
        self.X_ND_Values = 0.0
        self.Y_ND_Values = 0.0
        self.Z_ND_Values = 0.0





        self.ser = serial.Serial(self.port, self.baudrate, parity=self.parity, stopbits=self.stopbits,
                                 bytesize=self.bytesize, timeout=self.timeout)
        self.serial_lock = threading.Lock()

        self.read_values()


    def read_values(self):
        """To be called in Overview update method"""
        threading.Thread(target=self.read_x_value).start()
        threading.Thread(target=self.read_y_value).start()
        threading.Thread(target=self.read_z_value).start()
        # self.after(500, self.read_values)


    def read_x_value(self):
        command_rd = "RD DM01010\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
        response = response.decode().strip()
        value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
        if value:
            self.X_ND_Values = float(value)/100
        else:
            print("Invalid response:", response)

    def read_y_value(self):
        command_rd = "RD DM02010\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
        response = response.decode().strip()
        value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
        if value:
            self.X_ND_Values = float(value)/100
            # print("Y Value:", value)
        else:
            print("Invalid response:", response)
    def read_z_value(self):
        command_rd = "RD W0002\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
        response = response.decode().strip()
        value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
        if value:
            self.Z_ND_Values = (float(value) * 0.00018)
            # print("Z Value:", value)
        else:
            print("Invalid response:", response)

    def send_command(self, command):
        with self.serial_lock:
            self.ser.write(command.encode())

    def x_move_command(self,value):
        value = str(int(value) * 100)
        command_input = f"WR DM07000.L {value}\r"  # Input the desired X value
        self.send_command(command_input)
        # print("X Value", command_input)
        command_input_convert = "WR MR01000 1\r"
        self.send_command(command_input_convert)
        print("New X Value", command_input_convert)
        command_move = "WR MR05200 1\r"
        self.send_command(command_move)

    def y_move_command(self,value):
        value = str(int(value) * 100)
        command_input = f"WR DM02000.L {value}\r"  # Input the desired Y value
        self.send_command(command_input)
        # print("Y Value", command_input)
        command_input_convert = "WR MR03000 1\r"
        self.send_command(command_input_convert)
        # print("New Y Value", command_input_convert)
        command_move = "WR MR06200 1\r"
        self.send_command(command_move)

    def z_move_command(self,value):
        value = str(int(value) * 100)
        command_input = f"WR DM02030.L {value}\r"  # Input the desired Y value
        self.send_command(command_input)
        # print("Z Value", command_input)
        command_input_convert = "WR MR09000 1\r"
        self.send_command(command_input_convert)
        # print("New Z Value", command_input_convert)
        command_move = "WR MR04200 1\r"
        self.send_command(command_move)

    def send_needle_driver_reset_command(self, axis, command):
        if command == "START":
            if axis == "X":
                command_wr = "WR MR05000 1\r"
            elif axis == "Y":
                command_wr = "WR MR06000 1\r"
            elif axis == "Z":
                command_wr = "WR MR04000 1\r"
        elif command == "STOP":
            if axis == "X":
                command_wr = "WR MR05000 0\r"
            elif axis == "Y":
                command_wr = "WR MR06000 0\r"
            elif axis == "Z":
                command_wr = "WR MR04000 0\r"
        self.send_command(command_wr)

    def send_needle_driver_stop_command(self, axis, command):
        if command == "START":
            if axis == "X":
                command_wr = "WR MR05302 1\r"
            elif axis == "Y":
                command_wr = "WR MR06302 1\r"
            elif axis == "Z":
                command_wr = "WR MR04302 1\r"
        elif command == "STOP":
            if axis == "X":
                command_wr = "WR MR05302 0\r"
            elif axis == "Y":
                command_wr = "WR MR06302 0\r"
            elif axis == "Z":
                command_wr = "WR MR04302 0\r"
        self.send_command(command_wr)

    def send_needle_driver_home_command(self, axis, command):
        if command == "START":
            if axis == "X":
                command_wr_stop = "WR MR05100 1\r"
            elif axis == "Y":
                command_wr_stop = "WR MR06100 1\r"
            elif axis == "Z":
                command_wr_stop = "WR MR04100 1\r"
        elif command == "STOP":
            if axis == "X":
                command_wr_stop = "WR MR05100 0\r"
            elif axis == "Y":
                command_wr_stop = "WR MR06100 0\r"
            elif axis == "Z":
                command_wr_stop = "WR MR04100 0\r"
        self.send_command(command_wr_stop)

    def send_needle_driver_toggle_command(self, axis, command):
        if command == "START":
            if axis == "X+":
                command_wr = "WR MR05300 1\r"
            elif axis == "X-":
                command_wr = "WR MR05301 1\r"
            elif axis == "Y+":
                command_wr = "WR MR06300 1\r"
                # print(command_wr)
            elif axis == "Y-":
                command_wr = "WR MR06301 1\r"
            elif axis == "Z+":
                command_wr = "WR MR04300 1\r"
            elif axis == "Z-":
                command_wr = "WR MR04301 1\r"
        elif command == "STOP":
            if axis == "X+":
                command_wr = "WR MR05300 0\r"
            elif axis == "X-":
                command_wr = "WR MR05301 0\r"
            elif axis == "Y+":
                command_wr = "WR MR06300 0\r"
                # print(command_wr)
            elif axis == "Y-":
                command_wr = "WR MR06301 0\r"
            elif axis == "Z+":
                command_wr = "WR MR04300 0\r"
            elif axis == "Z-":
                command_wr = "WR MR04301 0\r"
        self.send_command(command_wr)

    def send_needle_driver_home_command(self, axis, command):
        if command == "START":
            if axis == "X":
                command_wr_stop = "WR MR05100 1\r"
            elif axis == "Y":
                command_wr_stop = "WR MR06100 1\r"
            elif axis == "Z":
                command_wr_stop = "WR MR04100 1\r"
        elif command == "STOP":
            if axis == "X":
                command_wr_stop = "WR MR05100 0\r"
            elif axis == "Y":
                command_wr_stop = "WR MR06100 0\r"
            elif axis == "Z":
                command_wr_stop = "WR MR04100 0\r"
        self.send_command(command_wr_stop)

    def send_needle_driver_reset_command(self,axis,command):
        if command == "START":
            if axis == "X":
                command_wr = "WR MR05000 1\r"
            elif axis == "Y":
                command_wr = "WR MR06000 1\r"
            elif axis == "Z":
                command_wr = "WR MR04000 1\r"
        elif command == "STOP":
            if axis == "X":
                command_wr = "WR MR05000 0\r"
            elif axis == "Y":
                command_wr = "WR MR06000 0\r"
            elif axis == "Z":
                command_wr = "WR MR04000 0\r"
        self.send_command(command_wr)