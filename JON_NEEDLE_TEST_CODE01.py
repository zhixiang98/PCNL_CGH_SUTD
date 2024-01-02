import tkinter as tk
from tkinter import ttk
import serial
import threading
import re
import time


class PLCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PLC App")
        self.stop_flag = False
        # Create buttons
        self.x_toggle = ttk.Button(self.root, text="X", command=self.toggle_x)
        self.x_toggle.grid(row=0, column=0, padx=10, pady=10)

        self.y_toggle = ttk.Button(self.root, text="Y", command=self.toggle_y)
        self.y_toggle.grid(row=0, column=1, padx=10, pady=10)

        self.z_toggle = ttk.Button(self.root, text="Z", command=self.toggle_z)
        self.z_toggle.grid(row=0, column=2, padx=10, pady=10)

        self.x2_toggle = ttk.Button(self.root, text="X2", command=self.toggle_x2)
        self.x2_toggle.grid(row=1, column=0, padx=10, pady=10)

        self.y2_toggle = ttk.Button(self.root, text="Y2", command=self.toggle_y2)
        self.y2_toggle.grid(row=1, column=1, padx=10, pady=10)

        self.z2_toggle = ttk.Button(self.root, text="Z2", command=self.toggle_z2)
        self.z2_toggle.grid(row=1, column=2, padx=10, pady=10)

        self.x_home = ttk.Button(self.root, text="X Home", command=self.toggle_x_home)
        self.x_home.grid(row=2, column=0, padx=10, pady=10)

        self.x_reset = ttk.Button(self.root, text="X Reset", command=self.reset_x)
        self.x_reset.grid(row=3, column=0, padx=10, pady=10)

        self.y_home = ttk.Button(self.root, text="Y Home", command=self.toggle_y_home)
        self.y_home.grid(row=2, column=1, padx=10, pady=10)

        self.y_reset = ttk.Button(self.root, text="Y Reset", command=self.reset_y)
        self.y_reset.grid(row=3, column=1, padx=10, pady=10)

        self.z_home = ttk.Button(self.root, text="Z Home", command=self.toggle_z_home)
        self.z_home.grid(row=2, column=2, padx=10, pady=10)

        self.z_reset = ttk.Button(self.root, text="Z Reset", command=self.reset_z)
        self.z_reset.grid(row=3, column=2, padx=10, pady=10)

        # Enter coordinates for move
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(self.root, textvariable=self.x_var)
        self.x_entry.grid(row=5, column=0, padx=10, pady=10)
        self.x_button = ttk.Button(self.root, text="Move X", command=self.x_move_command)
        self.x_button.grid(row=6, column=0, padx=10, pady=10)

        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(self.root, textvariable=self.y_var)
        self.y_entry.grid(row=5, column=1, padx=10, pady=10)
        self.y_button = ttk.Button(self.root, text="Move Y", command=self.y_move_command)
        self.y_button.grid(row=6, column=1, padx=10, pady=10)

        self.z_var = tk.StringVar()
        self.z_entry = ttk.Entry(self.root, textvariable=self.z_var)
        self.z_entry.grid(row=5, column=2, padx=10, pady=10)
        self.z_button = ttk.Button(self.root, text="Move Z", command=self.z_move_command)
        self.z_button.grid(row=6, column=2, padx=10, pady=10)

        self.all_home = ttk.Button(self.root, text="All Home", command=self.toggle_all_home)
        self.all_home.grid(row=7, column=0, padx=10, pady=10)

        self.move_button = ttk.Button(self.root, text="Move y then z", command=self.move_y_function)
        self.move_button.grid(row=7, column=1, padx=10, pady=10)

        self.move_button = ttk.Button(self.root, text="Move z then y", command=self.move_z_function)
        self.move_button.grid(row=7, column=2, padx=10, pady=10)

        self.x_stop = ttk.Button(self.root, text="Stop X", command=self.stop_x)
        self.x_stop.grid(row=8, column=0, padx=10, pady=10)
        self.y_stop = ttk.Button(self.root, text="Stop Y", command=self.stop_y)
        self.y_stop.grid(row=8, column=1, padx=10, pady=10)
        self.z_stop = ttk.Button(self.root, text="Stop Z", command=self.stop_z)
        self.z_stop.grid(row=8, column=2, padx=10, pady=10)

        # Create labels
        self.x_label = ttk.Label(self.root, text="X Value: ")
        self.x_label.grid(row=4, column=0, padx=10, pady=10)

        self.y_label = ttk.Label(self.root, text="Y Value: ")
        self.y_label.grid(row=4, column=1, padx=10, pady=10)

        self.z_label = ttk.Label(self.root, text="Z Value: ")
        self.z_label.grid(row=4, column=2, padx=10, pady=10)

        # Serial port settings
        self.port = "COM3"
        self.baudrate = 9600
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.timeout = 0.1  # Specify the timeout value in seconds

        # Initialize the serial port
        self.ser = serial.Serial(self.port, self.baudrate, parity=self.parity, stopbits=self.stopbits,
                                 bytesize=self.bytesize, timeout=self.timeout)

        # Create a lock for serial port access
        self.serial_lock = threading.Lock()

        # Start reading values asynchronously
        self.read_values()

        self.move_command_active = False

    def send_command(self, command):
        with self.serial_lock:
            self.ser.write(command.encode())

    def toggle_x(self):
        if self.x_toggle["text"] == "X":
            self.send_x_command()
            self.x_toggle["text"] = "X OFF"
        else:
            self.send_x_command_stop()
            self.x_toggle["text"] = "X"

    def toggle_y(self):
        if self.y_toggle["text"] == "Y":
            self.send_y_command()
            self.y_toggle["text"] = "Y OFF"
        else:
            self.send_y_command_stop()
            self.y_toggle["text"] = "Y"

    def toggle_z(self):
        if self.z_toggle["text"] == "Z":
            self.send_z_command()
            self.z_toggle["text"] = "Z OFF"
        else:
            self.send_z_command_stop()
            self.z_toggle["text"] = "Z"

    def toggle_x2(self):
        if self.x2_toggle["text"] == "X2":
            self.send_x2_command()
            self.x2_toggle["text"] = "X2 OFF"
        else:
            self.send_x2_command_stop()
            self.x2_toggle["text"] = "X2"

    def toggle_y2(self):
        if self.y2_toggle["text"] == "Y2":
            self.send_y2_command()
            self.y2_toggle["text"] = "Y2 OFF"
        else:
            self.send_y2_command_stop()
            self.y2_toggle["text"] = "Y2"

    def toggle_z2(self):
        if self.z2_toggle["text"] == "Z2":
            self.send_z2_command()
            self.z2_toggle["text"] = "Z2 OFF"
        else:
            self.send_z2_command_stop()
            self.z2_toggle["text"] = "Z2"

    def toggle_x_home(self):
        if self.x_home["text"] == "X Home":
            self.home_x()
            self.x_home["text"] = "X Home OFF"
        else:
            self.home_x_stop()
            self.x_home["text"] = "X Home"

    def toggle_y_home(self):
        if self.y_home["text"] == "Y Home":
            self.home_y()
            self.y_home["text"] = "Y Home OFF"
        else:
            self.home_y_stop()
            self.y_home["text"] = "Y Home"

    def toggle_z_home(self):
        if self.z_home["text"] == "Z Home":
            self.home_z()
            self.z_home["text"] = "Z Home OFF"
        else:
            self.home_z_stop()
            self.z_home["text"] = "Z Home"

    def toggle_x_reset(self):
        if self.x_reset["text"] == "X Reset":
            self.reset_x()
            self.x_reset["text"] = "X Reset OFF"
        else:
            self.reset_x_stop()
            self.x_reset["text"] = "X Reset"

    def toggle_y_reset(self):
        if self.y_reset["text"] == "Y Reset":
            self.reset_y()
            self.y_reset["text"] = "Y Reset OFF"
        else:
            self.reset_y_stop()
            self.y_reset["text"] = "Y Reset"

    def toggle_z_reset(self):
        if self.z_reset["text"] == "Z Reset":
            self.reset_z()
            self.z_reset["text"] = "Z Reset OFF"
        else:
            self.reset_z_stop()
            self.z_reset["text"] = "Z Reset"

    def toggle_all_home(self):
        if self.all_home["text"] == "All Home":
            self.home_z()
            self.home_y()
            self.home_x()
            self.all_home["text"] = "All Home OFF"
        else:
            self.home_z_stop()
            self.home_y_stop()
            self.home_x_stop()
            self.all_home["text"] = "All Home"

    def send_x_command(self):
        command_wr = "WR MR05300 1\r"
        self.send_command(command_wr)

    def send_x_command_stop(self):
        command_wr_stop = "WR MR05300 0\r"
        self.send_command(command_wr_stop)

    def send_x2_command(self):
        command_wr = "WR MR05301 1\r"
        self.send_command(command_wr)

    def send_x2_command_stop(self):
        command_wr_stop = "WR MR05301 0\r"
        self.send_command(command_wr_stop)

    def send_y_command(self):
        command_wr = "WR MR06300 1\r"
        self.send_command(command_wr)

    def send_y_command_stop(self):
        command_wr_stop = "WR MR06300 0\r"
        self.send_command(command_wr_stop)

    def send_y2_command(self):
        command_wr = "WR MR06301 1\r"
        self.send_command(command_wr)

    def send_y2_command_stop(self):
        command_wr_stop = "WR MR06301 0\r"
        self.send_command(command_wr_stop)

    def send_z_command(self):
        command_wr = "WR MR04300 1\r"
        self.send_command(command_wr)

    def send_z_command_stop(self):
        command_wr_stop = "WR MR04300 0\r"
        self.send_command(command_wr_stop)

    def send_z2_command(self):
        command_wr = "WR MR04301 1\r"
        self.send_command(command_wr)

    def send_z2_command_stop(self):
        command_wr_stop = "WR MR04301 0\r"
        self.send_command(command_wr_stop)

    def reset_x(self):
        command_wr = "WR MR05000 1\r"
        self.send_command(command_wr)

    def reset_x_stop(self):
        command_wr = "WR MR05000 0\r"
        self.send_command(command_wr)

    def home_x(self):

        command_wr_stop = "WR MR05100 1\r"
        self.send_command(command_wr_stop)

    def home_x_stop(self):
        command_wr_stop = "WR MR05100 0\r"
        self.send_command(command_wr_stop)

    def reset_y(self):
        command_wr = "WR MR06000 1\r"
        self.send_command(command_wr)

    def reset_y_stop(self):
        command_wr = "WR MR06000 0\r"
        self.send_command(command_wr)

    def home_y(self):
        command_wr_stop = "WR MR06100 1\r"
        self.send_command(command_wr_stop)

    def home_y_stop(self):
        command_wr_stop = "WR MR06100 0\r"
        self.send_command(command_wr_stop)

    def reset_z(self):
        command_wr = "WR MR04000 1\r"
        self.send_command(command_wr)

    def reset_z_stop(self):
        command_wr = "WR MR04000 0\r"
        self.send_command(command_wr)

    def home_z(self):
        command_wr_stop = "WR MR04100 1\r"
        self.send_command(command_wr_stop)

    def home_z_stop(self):
        command_wr_stop = "WR MR04100 0\r"
        self.send_command(command_wr_stop)

    def stop_x(self):
        command_wr_stop = "WR MR05302 1\r"
        self.send_command(command_wr_stop)

    def stop_y(self):
        command_wr_stop = "WR MR06302 1\r"
        self.send_command(command_wr_stop)
        print("Stopping Y")

    def stop_z(self):
        command_wr_stop = "WR MR04302 1\r"
        self.send_command(command_wr_stop)

    def read_values(self):
        self.read_x_value()
        self.read_y_value()
        self.read_z_value()
        self.root.after(500, self.read_values)

    def read_x_value(self):
        command_rd = "RD DM01010\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
        response = response.decode().strip()
        value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
        if value:
            self.x_label["text"] = "X Value: " + str(float(value) / 100)
            print("X Value:", value)
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
            self.y_label["text"] = "Y Value: " + str(float(value) / 100)
            print("Y Value:", value)
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
            self.z_label["text"] = "Z Value: " + str(float(value) * 0.01)
            print("Z Value:", value)
        else:
            print("Invalid response:", response)

    def x_move_command(self):
        value = self.x_entry.get()
        print(value)
        value = str(int(float(value) * 100))
        command_input = f"WR DM07000.L {value}\r"  # Input the desired Y value
        self.send_command(command_input)
        print("X Value", command_input)
        command_input_convert = "WR MR01000 1\r"
        self.send_command(command_input_convert)
        print("New X Value", command_input_convert)
        command_move = "WR MR05200 1\r"
        self.send_command(command_move)

    def y_move_command(self):
        value = self.y_entry.get()
        print(value)
        value = str(int(float(value) * 100))
        command_input = f"WR DM02000.L {value}\r"  # Input the desired Y value
        self.send_command(command_input)
        print("Y Value", command_input)
        command_input_convert = "WR MR03000 1\r"
        self.send_command(command_input_convert)
        print("New Y Value", command_input_convert)
        command_move = "WR MR06200 1\r"
        self.send_command(command_move)

    def z_move_command(self):
        value = self.z_entry.get()
        value = str(int(float(value) * 100))
        command_input = f"WR DM02030.L {value}\r"  # Input the desired Y value
        self.send_command(command_input)
        command_input_convert = "WR MR09000 1\r"
        self.send_command(command_input_convert)
        command_move = "WR MR04200 1\r"
        self.send_command(command_move)

    def move_y_function(self):
        self.y_move_command()
        self.execute_move_z()

    def execute_move_z(self):
        self.wait_for_y_value(1)
        self.z_move_command()

    def wait_for_y_value(self, target_value):
        while True:
            response = self.read_y_response()  # Replace this with your response reading logic
            value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
            if value:
                print("Current Value:", value)
                if float(value) == target_value:
                    break  # Exit the loop if the target value is reached
            time.sleep(0.5)  # Adjust the delay time as needed (e.g., 0.1 for 100 ms)

    def read_y_response(self):
        command_rd = "RD CR8501\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
            print(response)
        return response.decode().strip()

    def move_z_function(self):
        self.z_move_command()
        self.execute_move_y()

    def execute_move_y(self):
        Z_value = float(self.z_entry.get())
        if Z_value < 10:
            Z_value = str("00") + str(int((Z_value) * 100))
        else:
            Z_value = str("0") + str(int((Z_value) * 100))
        print("Z_value:", Z_value)
        self.wait_for_z_value(Z_value)
        self.y_move_command()

    def wait_for_z_value(self, target_value):
        while True:
            response = self.read_z_response()  # Replace this with your response reading logic
            value = re.sub("[^0-9.]", "", response)  # Remove non-numeric characters
            if value:
                print("Current Value:", response)
                if str(value) == target_value:
                    break  # Exit the loop if the target value is reached
            time.sleep(0.5)  # Adjust the delay time as needed (e.g., 0.1 for 100 ms)

    def read_z_response(self):
        command_rd = "RD W0002\r"
        with self.serial_lock:
            self.ser.write(command_rd.encode())
            response = self.ser.read(100)
            print(response)
        return response.decode().strip()


root = tk.Tk()
app = PLCApp(root)
root.mainloop()

"""""
x jog: "WR MR05300 1\r"
(x jog off: "WR MR05300 0\r")
x2 jog: "WR MR05301 1\r"

Y jog: "WR MR06300 1\r"
Y2 jog: "WR MR06301 1\r"

Z jog: "WR MR04300 1\r"
Z2 jog: "WR MR04301 1\r"

Reset X: "WR MR05000 1\r"
Reset Y: "WR MR06000 1\r"
Reset Z: "WR MR04000 1\r"

Home X: "WR MR05100 1\r"
Home Y: "WR MR06100 1\r"
Home Z: "WR MR04100 1\r"

Read X: "RD DM01010\r"
Read Y: "RD DM02010\r"
Read Z: "RD W0002\r"

Move X: f"WR DM07000.L {value}\r", "WR MR01000 1\r", "WR MR05200 1\r" (input, convert, publish)
Move Y: f"WR DM02000.L {value}\r", "WR MR03000 1\r", "WR MR06200 1\r"
Move Z: f"WR DM02030.L {value}\r", "WR MR09000 1\r", "WR MR04200 1\r"   

Check if process running: "RD CR8501\r"

Stop X: "WR MR05302 1"
Stop Y: "WR MR06302 1"
Stop Z: "WR MR04302 1"

"""""
