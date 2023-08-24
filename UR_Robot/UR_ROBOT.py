from PCNL_CGH_SUTD.rtde import rtde, rtde_config
import PCNL_CGH_SUTD.UR_Robot.constants as c
import sys
import numpy as np
"""Class that manages the UR_Robot in general.Relies on the rtde package
    ....
    Constants
    -----------
    ROBOT_IP: str
        Robot IP address must be the same on UR Settings.
    ROBOT_PORT: int
        30004 for RTDE communication
    CONFIG_FILE: str
        Location of config file. Config file written in .xml format
    REGISTER_ROUNDING_DP:int
        Rounding decimal points to
    """


class UR_ROBOT():
    #Initialise the UR ROBOT class
    def __init__(self, ROBOT_IP, Config_File):
        self.state = None
        self.ROBOT_HOST = c.ROBOT_IP
        self.ROBOT_PORT = c.ROBOT_PORT
        self.config_filename = c.CONFIG_FILE
        self.conf = rtde_config.ConfigFile(self.config_filename)
        self.state_names, self.state_types = self.conf.get_recipe('state')
        self.setp_names, self.setp_types = self.conf.get_recipe('setp')
        self.watchdog_names, self.watchdog_types = self.conf.get_recipe('watchdog')

        self.con = rtde.RTDE(self.ROBOT_HOST, self.ROBOT_PORT)
        self.connction_state = self.con.connect()

        print("--successful connected")  # TODO maybe can add logging. KIV.

        self.con.send_output_setup(self.state_names, self.state_types, 500) #last argument is frequency
        self.setp = self.con.send_input_setup(self.setp_names, self.setp_types)
        self.watchdog = self.con.send_input_setup(self.watchdog_names, self.watchdog_types)

        # Initialising all variables to zero
        self.setp.input_double_register_0 = 0
        self.setp.input_double_register_1 = 0
        self.setp.input_double_register_2 = 0
        self.setp.input_double_register_3 = 0
        self.setp.input_double_register_4 = 0
        self.setp.input_double_register_5 = 0

        self.setp.input_bit_registers0_to_31 = 0

        self.watchdog.input_int_register_0 = 0

        if not self.con.send_start():
            sys.exit()

    def Update_Date(self):
        # Create a dictionary to store the useful robot data, return dictionary at the end
        # Dictionary values include TCP_POS, Robot_Output's double register, Robot Output's Output integer register
        dict = {}
        self.state = self.con.receive()
        pos = self.state.actual_TCP_pose
        pos = list(np.around(np.array(pos),5)) # rounding to 5dp
        dict["TCP_POS"] = pos

        dict["input_double_register0"] = round(self.state.output_double_register_0, c.REGISTER_ROUNDING_DP)
        dict["input_double_register1"] = round(self.state.output_double_register_1, c.REGISTER_ROUNDING_DP)
        dict["input_double_register2"] = round(self.state.output_double_register_2, c.REGISTER_ROUNDING_DP)
        dict["input_double_register3"] = round(self.state.output_double_register_3, c.REGISTER_ROUNDING_DP)
        dict["input_double_register4"] = round(self.state.output_double_register_4, c.REGISTER_ROUNDING_DP)
        dict["input_double_register5"] = round(self.state.output_double_register_5, c.REGISTER_ROUNDING_DP)

        dict["input_integer_register0"] = self.state.output_int_register_0  # this is used in computer to tell that process has complete on UR
        dict["output_bit_registers0_to_31"] = self.state.output_bit_registers0_to_31

        return dict

    def setp_to_list(self):
        # converts the data setp from the UR to list
        List = []
        for i in range(0,6):
            List.append(self.setp.__dict__["input_double_register_%i" % i])
        return List

    def list_to_setp(self, List):
        # converts list to setp to send to UR_Robot
        for i in range(0,6):
            self.setp.__dict__["input_double_register_%i" % i] = List[i] #Check this _%i
        return self.setp
