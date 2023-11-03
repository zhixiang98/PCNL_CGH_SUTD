
import time
import tkinter
import GUI.Frame.constants as c
import UR_Robot.UR_ROBOT
import cv2
import PIL.Image, PIL.ImageTk
import threading
from tkinter import ttk
import US_Screen.US_Image
import Needle_Driver.NeedleDriver_Controller as ND

# from ...GUI.Frame import constants as c
# from ...UR_Robot.UR_ROBOT import UR_ROBOT
# from ...US_Screen import US_Image
# import Needle


class Overview(tkinter.Frame):

    def __init__(self, parent, cont):
        tkinter.Frame.__init__(self, parent)
        self.main_image = None
        self.igtl_initialised = False
        # US_Screen.US_Image.US_IMAGE.__init__(self)
        self.US_image = None

        self.display = None
        self.cont = cont
        self.delay = c.REFRESH_DELAY

        # --- Tkinter Variables ---
        # """Tkinter Variables will be in CAPs"""
        self.MILIMTR_PER_PIXEL = tkinter.DoubleVar()

        self.X_US_COORDINATES, self.Y_US_COORDINATES = tkinter.DoubleVar(), tkinter.DoubleVar()
        self.ALPHA = tkinter.DoubleVar()

        self.X_US_SURFACE_TARGET_COORDINATES, self.Y_US_SURFACE_TARGET_COORDINATES = tkinter.DoubleVar(), tkinter.DoubleVar()

        # Offset x distance and d distance
        self.OFFSET_X_DISTANCE = tkinter.DoubleVar()
        self.OFFSET_D_DISTANCE = tkinter.DoubleVar()

        # MOVE_DISTANCE_ACTUATOR is the number to key into the actuator controller
        self.MOVE_DISTANCE_ACTUATOR = tkinter.DoubleVar()

        # MOVE_UR_ROBOT by this (units in mm)
        self.MOVE_UR_ROBOT_BY = tkinter.DoubleVar()

        # --- Tkinter Elements ---
        # CANVAS will be to display the image
        # CANVAS will be to display the image
        self.Canvas = tkinter.Canvas(self, bg=c.CANVAS_BG, height=c.CANVAS_HEIGHT, width=c.CANVAS_WIDTH, bd=c.CANVAS_BD,
                                     highlightthickness=c.CANVAS_HIGHLIGHT, relief=c.CANVAS_RELIEF)
        self.Canvas.grid(row=c.CANVAS_ROW, column=c.CANVAS_COLUMN)

        self.Image_Setting_Label_Frame = tkinter.LabelFrame(self, text='Image Settings')
        self.Image_Setting_Label_Frame.place(x=c.IMAGE_SETTING_LBL_FRAME_X, y=c.IMAGE_SETTING_LBL_FRAME_Y,
                                             width=c.IMAGE_SETTING_LBL_FRAME_WIDTH,
                                             height=c.IMAGE_SETTING_LBL_FRAME_HEIGHT)

        # -- Image_Setting_Label_Frame---
        self.Select_Origin_Button = tkinter.Button(self.Image_Setting_Label_Frame, text=c.ORIGIN_BUTTON_TEXT,
                                                   width=c.BUTTON_WIDTH,
                                                   command=lambda: self.Select_Origin_Button_Function())
        self.Select_Origin_Button.grid(row=c.ORIGIN_BUTTON_ROW, column=c.ORIGIN_BUTTON_COLUMN, padx=c.PADX, pady=c.PADY)

        self.Select_Target_Button = tkinter.Button(self.Image_Setting_Label_Frame, text=c.SELECT_TARGET_BUTTON_TEXT,
                                                   width=c.BUTTON_WIDTH, command=lambda: self.Select_Target())
        self.Select_Target_Button.grid(row=c.SELECT_TARGET_BUTTON_ROW, column=c.SELECT_TARGET_BUTTON_COLUMN,
                                       padx=c.PADX, pady=c.PADY)

        self.Alpha_Button = tkinter.Button(self.Image_Setting_Label_Frame, text=c.ALPHA_BUTTON_TEXT,
                                           command=lambda: self.calculate_target_ange(), width=c.BUTTON_WIDTH)
        self.Alpha_Button.grid(row=c.ALPHA_BUTTON_ROW, column=c.ALPHA_BUTTON_COLUMN, padx=c.PADX,
                               pady=c.PADY)

        self.Draw_Needle_Button = tkinter.Button(self.Image_Setting_Label_Frame, text=c.DRAW_NEEDLE_BUTTON_TEXT,
                                                 command=lambda: self.Draw_Needle_Button_Function(),
                                                 width=c.BUTTON_WIDTH)
        self.Draw_Needle_Button.grid(row=c.DRAW_NEEDLE_BUTTON_ROW, column=c.DRAW_NEEDLE_BUTTON_COLUMN, padx=c.PADX,
                                     pady=c.PADY)

        self.Convert_Pixel2Coordinates_Button = tkinter.Button(self.Image_Setting_Label_Frame,
                                                               text=c.CONVERT_PIXEL2COORDINATES_TEXT,
                                                               command=lambda: self.convert_pixel_to_US_coord(),
                                                               width=c.BUTTON_WIDTH)
        self.Convert_Pixel2Coordinates_Button.grid(row=c.CONVERT_PIXEL2COORDINATES_ROW,
                                                   column=c.CONVERT_PIXEL2COORDINATES_COLUMN, padx=c.PADX, pady=c.PADY)

        self.Milimeter_Per_Pixel_Entry = tkinter.Entry(self.Image_Setting_Label_Frame,
                                            textvariable=str(self.MILIMTR_PER_PIXEL))
        self.Milimeter_Per_Pixel_Entry.grid(row=c.DEPTH_COMBO_BOX_ROW, column=c.DEPTH_COMBO_BOX_COLUMN, padx=c.PADX, pady=c.PADY)

        self.Connect_IGTL_Button = tkinter.Button(self.Image_Setting_Label_Frame, text=c.RECONNECT_IMAGE_TEXT,
                                                  command=lambda: self.connection_igtl_client(), width=c.BUTTON_WIDTH)
        self.Connect_IGTL_Button.grid(row=c.CONNECT_IGT_BUTTON_ROW, column=c.CONNECT_IGT_BUTTON_COLUMN)

        self.Image_Two_Screen_Freeze_Button = tkinter.Button(self.Image_Setting_Label_Frame, text = "IMG2 Freeze", command = lambda: self.freeze_frame(2), width = c.BUTTON_WIDTH)
        self.Image_Two_Screen_Freeze_Button.grid(row = c.IMAGE_TWO_SCREEN_FREEZE_BUTTON_ROW, column = c.IMAGE_TWO_SCREEN_FREEZE_BUTTON_COLUMN)

        self.Image_Four_Screen_Freeze_Button = tkinter.Button(self.Image_Setting_Label_Frame, text="IMG4 Freeze",
                                                             command=lambda: self.freeze_frame(4), width=c.BUTTON_WIDTH)
        self.Image_Four_Screen_Freeze_Button.grid(row=c.IMAGE_FOUR_SCREEN_FREEZE_BUTTON_ROW,
                                                 column=c.IMAGE_FOUR_SCREEN_FREEZE_BUTTON_COLUMN)

        # --- CB tkinter variables---
        self.Show_Origin_CB_Var = tkinter.IntVar()
        self.Show_Needle_CB_Line_Var = tkinter.IntVar()
        self.Show_Target_CB_Var = tkinter.IntVar()
        self.Show_US_Coord_CB_Var = tkinter.IntVar()
        self.Show_Projected_Line_CB_Var = tkinter.IntVar()
        self.Show_Stacked_Images_CB_Var = tkinter.IntVar()

        # --- CB tkinter ----
        self.show_projected_line_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_projected_line",
                                                          variable=self.Show_Projected_Line_CB_Var, onvalue=1,
                                                          offvalue=0)
        self.show_projected_line_CB.grid(row=c.SHOW_PROJECTED_LINE_CB_ROW, column=c.SHOW_PROJECTED_LINE_CB_COLUMN,
                                         padx=20, columnspan=2, sticky="w")

        self.show_origin_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_origin",
                                                  variable=self.Show_Origin_CB_Var, onvalue=1,
                                                  offvalue=0)
        self.show_origin_CB.grid(row=c.SHOW_ORIGIN_CB_ROW, column=c.SHOW_ORIGIN_CB_COLUMN, padx=20)

        self.show_needle_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_needle",
                                                  variable=self.Show_Needle_CB_Line_Var,
                                                  onvalue=1, offvalue=0)
        self.show_needle_CB.grid(row=c.SHOW_NEEDLE_CB_ROW, column=c.SHOW_NEEDLE_CB_COLUMN, padx=20)

        self.show_target_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_target",
                                                  variable=self.Show_Target_CB_Var,
                                                  onvalue=1, offvalue=0)
        self.show_target_CB.grid(row=c.SHOW_TARGET_CB_ROW, column=c.SHOW_TARGET_CB_COLUMN, padx=20)

        self.show_US_Coord_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_coordinates",
                                                    variable=self.Show_US_Coord_CB_Var,
                                                    onvalue=1, offvalue=0)
        self.show_US_Coord_CB.grid(row=c.SHOW_US_COORD_CB_ROW, column=c.SHOW_US_COORD_CB_COLUMN, padx=20)

        self.show_stacked_images_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text = "stacked_images", variable = self.Show_Stacked_Images_CB_Var, onvalue=1, offvalue=0)
        self.show_stacked_images_CB.grid(row = c.SHOW_STACKED_IMAGES_CB_ROW, column = c.SHOW_STACKED_IMAGES_CB_COLUMN, padx = 20)
        # --------US_INFO_LABEL_FRAME--------------

        self.US_INFO_LABEL_FRAME = tkinter.LabelFrame(self, text="Ultrasound Information")
        self.US_INFO_LABEL_FRAME.place(x=c.US_INFO_FRAME_X, y=c.US_INFO_FRAME_Y, width=c.US_INFO_FRAME_WIDTH,
                                       height=c.US_INFO_FRAME_HEIGHT)

        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.X_US_COORDINATES).grid(row=2, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, text="X US Coordinates: ").grid(row=1, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="Y US Coordinates: ").grid(row=3, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.Y_US_COORDINATES).grid(row=4, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="ALPHA: ").grid(row=5, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.ALPHA).grid(row=6, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="X Surface Coordinates: ").grid(row=7, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.X_US_SURFACE_TARGET_COORDINATES).grid(row=8, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="Y Surface Coordinates: ").grid(row=9, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.Y_US_SURFACE_TARGET_COORDINATES).grid(row=10,
                                                                                                        column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="offset x distance: ").grid(row=11, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.OFFSET_X_DISTANCE).grid(row=12, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="offset d distance: ").grid(row=13, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.OFFSET_D_DISTANCE).grid(row=14, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="move actuator distance: ").grid(row=15, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.MOVE_DISTANCE_ACTUATOR).grid(row=16, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="move UR Robot by: ").grid(row=17, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.MOVE_UR_ROBOT_BY).grid(row=18, column=1)

        # ---Tkinter Variables ---
        self.X_DISTANCE_TO_MOVE = tkinter.DoubleVar()
        self.TCP_TEXT_VARIABLE = tkinter.StringVar()
        self.INPUT_REGISTER00 = tkinter.DoubleVar()
        self.INPUT_REGISTER01 = tkinter.DoubleVar()
        self.INPUT_REGISTER02 = tkinter.DoubleVar()
        self.INPUT_REGISTER03 = tkinter.DoubleVar()
        self.INPUT_REGISTER04 = tkinter.DoubleVar()
        self.INPUT_REGISTER05 = tkinter.DoubleVar()

        self.Robot_Data_Frame = tkinter.LabelFrame(self, text="Robot Data Information")
        self.Robot_Data_Frame.place(x=c.ROBOT_DATA_FRAME_X, y=c.ROBOT_DATA_FRAME_Y, width=c.ROBOT_DATA_FRAME_WIDTH,
                                    height=c.ROBOT_DATA_FRAME_HEIGHT)

        self.Robot_TCP_Frame = tkinter.LabelFrame(self.Robot_Data_Frame, text="Robot TCP")
        self.Robot_TCP_Frame.place(x=0, y=50, width=525, height=50)

        tkinter.Label(self.Robot_TCP_Frame, textvariable=self.TCP_TEXT_VARIABLE, anchor='w').grid()

        self.Robot_Input_Frame = tkinter.LabelFrame(self.Robot_Data_Frame, text="Input Register")
        self.Robot_Input_Frame.place(x=0, y=100, width=525, height=80)

        tkinter.Label(self.Robot_Input_Frame, text='Register 0').grid(row=1, column=1, padx=15)
        tkinter.Label(self.Robot_Input_Frame, text='Register 1').grid(row=1, column=2, padx=15)
        tkinter.Label(self.Robot_Input_Frame, text='Register 2').grid(row=1, column=3, padx=15)
        tkinter.Label(self.Robot_Input_Frame, text='Register 3').grid(row=1, column=4, padx=15)
        tkinter.Label(self.Robot_Input_Frame, text='Register 4').grid(row=1, column=5, padx=15)
        tkinter.Label(self.Robot_Input_Frame, text='Register 5').grid(row=1, column=6, padx=15)

        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER00).grid(row=2, column=1)
        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER01).grid(row=2, column=2)
        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER02).grid(row=2, column=3)
        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER03).grid(row=2, column=4)
        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER04).grid(row=2, column=5)
        tkinter.Label(self.Robot_Input_Frame, textvariable=self.INPUT_REGISTER05).grid(row=2, column=6)

        self.Robot_Output_Frame = tkinter.LabelFrame(self.Robot_Data_Frame, text="Output Register")
        self.Robot_Output_Frame.place(x=0, y=155, width=525, height=100)
        tkinter.Label(self.Robot_Output_Frame, text='Register 0').grid(row=1, column=1, padx=15)
        tkinter.Label(self.Robot_Output_Frame, text='Register 1').grid(row=1, column=2, padx=15)
        tkinter.Label(self.Robot_Output_Frame, text='Register 2').grid(row=1, column=3, padx=15)
        tkinter.Label(self.Robot_Output_Frame, text='Register 3').grid(row=1, column=4, padx=15)
        tkinter.Label(self.Robot_Output_Frame, text='Register 4').grid(row=1, column=5, padx=15)
        tkinter.Label(self.Robot_Output_Frame, text='Register 5').grid(row=1, column=6, padx=15)

        self.OUTPUT_DB_REG0 = tkinter.DoubleVar()
        self.OUTPUT_DB_REG1 = tkinter.DoubleVar()
        self.OUTPUT_DB_REG2 = tkinter.DoubleVar()
        self.OUTPUT_DB_REG3 = tkinter.DoubleVar()
        self.OUTPUT_DB_REG4 = tkinter.DoubleVar()
        self.OUTPUT_DB_REG5 = tkinter.DoubleVar()

        self.ENTRY_REG0 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG0), width=10)
        self.ENTRY_REG1 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG1), width=10)
        self.ENTRY_REG2 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG2), width=10)
        self.ENTRY_REG3 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG3), width=10)
        self.ENTRY_REG4 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG4), width=10)
        self.ENTRY_REG5 = tkinter.Entry(self.Robot_Output_Frame, textvariable=str(self.OUTPUT_DB_REG5), width=10)

        self.ENTRY_REG0.grid(row=2, column=1)
        self.ENTRY_REG1.grid(row=2, column=2)
        self.ENTRY_REG2.grid(row=2, column=3)
        self.ENTRY_REG3.grid(row=2, column=4)
        self.ENTRY_REG4.grid(row=2, column=5)
        self.ENTRY_REG5.grid(row=2, column=6)

        # ----Buttons for Robot Frame ----
        self.Submit_Output_Button = tkinter.Button(self.Robot_Output_Frame, width=c.BUTTON_WIDTH,
                                                   text=c.SUBMIT_OUTPUT_BUTTON_TEXT,
                                                   command=lambda: self.Robot_Send_Output())
        self.Submit_Output_Button.grid(row=c.SUBMIT_OUTPUT_BUTTON_ROW, column=c.SUBMIT_OUTPUT_BUTTON_COLUMN,
                                       columnspan=2)

        self.Populate_Field_Button = tkinter.Button(self.Robot_Output_Frame, width=20, text="One Button",
                                                    command=lambda: self.Populate_Field())
        self.Populate_Field_Button.grid(row=c.POPULATE_BUTTON_ROW, column=c.POPULATE_BUTTON_COLUMN, columnspan=2)

        # ---------UR_ROBOT_IP Frame--------------
        self.Robot_IP_Frame = tkinter.LabelFrame(self.Robot_Data_Frame, text=c.ROBOT_IP_FRAME_TEXT)
        self.Robot_IP_Frame.place(x=c.ROBOT_IP_FRAME_X, y=c.ROBOT_IP_FRAME_Y, width=c.ROBOT_IP_FRAME_WIDTH,
                                  height=c.ROBOT_IP_FRAME_HEIGHT)

        self.IP_Text_Variable = tkinter.StringVar()
        self.IP_Address_Label = tkinter.Label(self.Robot_IP_Frame, text="IP_ADDRESS")
        self.IP_Address_Label.grid(row=0, column=0)

        self.IP_Address_Entry = tkinter.Entry(self.Robot_IP_Frame, textvariable=self.IP_Text_Variable)
        self.IP_Address_Entry.grid(row=0, column=1)

        self.IP_Address_Confirm_Button = tkinter.Button(self.Robot_IP_Frame, text="Connect Robot",
                                                        command=lambda: self.Robot_Connect_Button())
        self.IP_Address_Confirm_Button.grid(row=0, column=2)

        self.UR_MODE = tkinter.IntVar()

        self.UR_MODE_ENTRY = tkinter.Entry(self.Robot_IP_Frame, textvariable=str(self.UR_MODE))
        self.UR_MODE_ENTRY.grid(row=0, column=4, padx=10)

        self.UR_MODE_BUTTON = tkinter.Button(self.Robot_IP_Frame, text="MODE",
                                             command=lambda: self.Robot_Change_Mode(self.UR_MODE.get()))
        self.UR_MODE_BUTTON.grid(row=0, column=5)

        # ------NeedleDriver Controller--------------

        # --Tkinter Variable_X_Axis
        self.X_NEEDLE_VAR = tkinter.StringVar()
        # --X_Axis_Element
        self.NEEDLE_DRIVER_FRAME = tkinter.LabelFrame(self, text="Needle Driver")
        self.NEEDLE_DRIVER_FRAME.place(x=c.NEEDLE_DRIVER_FRAME_X, y=c.NEEDLE_DRIVER_FRAME_Y,
                                       height=c.NEEDLE_DRIVER_FRAME_HEIGHT, width=c.NEEDLE_DRIVER_FRAME_WIDTH)

        self.NEEDLE_X_MOVE_FRAME = tkinter.LabelFrame(self.NEEDLE_DRIVER_FRAME, text="X_Axis")
        self.NEEDLE_X_MOVE_FRAME.place(x=c.NEEDLE_DRIVER_X_DIR_MOVE_FRAME_X, y=c.NEEDLE_DRIVER_X_DIR_MOVE_FRAME_Y,
                                       width=c.NEEDLE_DRIVER_X_DIR_MOVE_FRAME_WIDTH,
                                       height=c.NEEDLE_DRIVER_X_DIR_MOVE_FRAME_HEIGHT)

        self.X_PLUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="X+",
                                                   command=lambda: self.needle_driver_toggle_button("X+"), padx=5,
                                                   pady=5)
        self.X_PLUS_TOGGLE_BUTTON.grid(row=0, column=0, sticky="nsew")

        self.X_MINUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="X-",
                                                    command=lambda: self.needle_driver_toggle_button("X-"), padx=5,
                                                    pady=5)
        self.X_MINUS_TOGGLE_BUTTON.grid(row=0, column=1, sticky="nsew")

        self.X_HOME_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="HOME",
                                                   command=lambda: self.needle_driver_home_button("X"),
                                                   padx=5, pady=5)
        self.X_HOME_TOGGLE_BUTTON.grid(row=0, column=2, sticky="nsew")

        self.X_RESET_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="RESET", padx=5, pady=5,
                                                    command=lambda: self.needle_driver_reset_button("X"))
        self.X_RESET_TOGGLE_BUTTON.grid(row=0, column=3, sticky="nsew")

        self.X_NEEDLE_ENTRY_BOX = tkinter.Entry(self.NEEDLE_X_MOVE_FRAME, textvariable=self.X_NEEDLE_VAR, width=10)
        self.X_NEEDLE_ENTRY_BOX.grid(row=0, column=4, padx=10)

        self.X_NEEDLE_MOVE_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="MOVE", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_move_button("X"))
        self.X_NEEDLE_MOVE_BUTTON.grid(row=0, column=5, sticky="nsew")

        self.X_NEEDLE_STOP_BUTTON = tkinter.Button(self.NEEDLE_X_MOVE_FRAME, text="STOP", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_stop_button("X"))
        self.X_NEEDLE_STOP_BUTTON.grid(row=0, column=6, sticky="nsew")

        self.X_Label_POSITION = tkinter.Label(self.NEEDLE_X_MOVE_FRAME, text="X Value: ")
        self.X_Label_POSITION.grid(row=0, column=7, sticky="nsew", padx=10)

        # --Tkinter Variable_Y_AYis
        self.Y_NEEDLE_VAR = tkinter.StringVar()
        # --Y_AYis_Element
        self.NEEDLE_Y_MOVE_FRAME = tkinter.LabelFrame(self.NEEDLE_DRIVER_FRAME, text="Y_Axis")
        self.NEEDLE_Y_MOVE_FRAME.place(x=c.NEEDLE_DRIVER_Y_DIR_MOVE_FRAME_X, y=c.NEEDLE_DRIVER_Y_DIR_MOVE_FRAME_Y,
                                       width=c.NEEDLE_DRIVER_Y_DIR_MOVE_FRAME_WIDTH,
                                       height=c.NEEDLE_DRIVER_Y_DIR_MOVE_FRAME_HEIGHT)

        self.Y_PLUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="Y+",
                                                   command=lambda: self.needle_driver_toggle_button("Y+"), padx=5,
                                                   pady=5)
        self.Y_PLUS_TOGGLE_BUTTON.grid(row=0, column=0, sticky="nsew")

        self.Y_MINUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="Y-",
                                                    command=lambda: self.needle_driver_toggle_button("Y-"), padx=5,
                                                    pady=5)
        self.Y_MINUS_TOGGLE_BUTTON.grid(row=0, column=1, sticky="nsew")

        self.Y_HOME_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="HOME", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_home_button("Y"))
        self.Y_HOME_TOGGLE_BUTTON.grid(row=0, column=2, sticky="nsew")

        self.Y_RESET_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="RESET", padx=5, pady=5,
                                                    command=lambda: self.needle_driver_reset_button("Y"))
        self.Y_RESET_TOGGLE_BUTTON.grid(row=0, column=3, sticky="nsew")

        self.Y_NEEDLE_ENTRY_BOX = tkinter.Entry(self.NEEDLE_Y_MOVE_FRAME, textvariable=self.Y_NEEDLE_VAR, width=10)
        self.Y_NEEDLE_ENTRY_BOX.grid(row=0, column=4, padx=10)

        self.Y_NEEDLE_MOVE_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="MOVE", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_move_button("Y"))
        self.Y_NEEDLE_MOVE_BUTTON.grid(row=0, column=5, sticky="nsew")

        self.Y_NEEDLE_STOP_BUTTON = tkinter.Button(self.NEEDLE_Y_MOVE_FRAME, text="STOP", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_stop_button("Y"))
        self.Y_NEEDLE_STOP_BUTTON.grid(row=0, column=6, sticky="nsew")

        self.Y_Label_POSITION = tkinter.Label(self.NEEDLE_Y_MOVE_FRAME, text="Y Value: ")
        self.Y_Label_POSITION.grid(row=0, column=7, sticky="nsew", padx=10)

        # --Tkinter Variable_Z_Axis
        self.Z_NEEDLE_VAR = tkinter.StringVar()
        # --Z_Axis_Element
        self.NEEDLE_Z_MOVE_FRAME = tkinter.LabelFrame(self.NEEDLE_DRIVER_FRAME, text="Z_Axis")
        self.NEEDLE_Z_MOVE_FRAME.place(x=c.NEEDLE_DRIVER_Z_DIR_MOVE_FRAME_X, y=c.NEEDLE_DRIVER_Z_DIR_MOVE_FRAME_Y,
                                       width=c.NEEDLE_DRIVER_Z_DIR_MOVE_FRAME_WIDTH,
                                       height=c.NEEDLE_DRIVER_Z_DIR_MOVE_FRAME_HEIGHT)

        self.Z_PLUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="Z+",
                                                   command=lambda: self.needle_driver_toggle_button("Z+"), padx=5,
                                                   pady=5)
        self.Z_PLUS_TOGGLE_BUTTON.grid(row=0, column=0, sticky="nsew")

        self.Z_MINUS_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="Z-",
                                                    command=lambda: self.needle_driver_toggle_button("Z-"), padx=5,
                                                    pady=5)
        self.Z_MINUS_TOGGLE_BUTTON.grid(row=0, column=1, sticky="nsew")

        self.Z_HOME_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="HOME", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_home_button("Z"))
        self.Z_HOME_TOGGLE_BUTTON.grid(row=0, column=2, sticky="nsew")

        self.Z_RESET_TOGGLE_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="RESET", padx=5, pady=5,
                                                    command=lambda: self.needle_driver_reset_button("Z"))
        self.Z_RESET_TOGGLE_BUTTON.grid(row=0, column=3, sticky="nsew")

        self.Z_NEEDLE_ENTRY_BOX = tkinter.Entry(self.NEEDLE_Z_MOVE_FRAME, textvariable=self.Z_NEEDLE_VAR, width=10)
        self.Z_NEEDLE_ENTRY_BOX.grid(row=0, column=4, padx=10)

        self.Z_NEEDLE_MOVE_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="MOVE", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_move_button("Z"))
        self.Z_NEEDLE_MOVE_BUTTON.grid(row=0, column=5, sticky="nsew")

        self.Z_NEEDLE_STOP_BUTTON = tkinter.Button(self.NEEDLE_Z_MOVE_FRAME, text="STOP", padx=5, pady=5,
                                                   command=lambda: self.needle_driver_stop_button("Z"))
        self.Z_NEEDLE_STOP_BUTTON.grid(row=0, column=6, sticky="nsew")

        self.Z_Label_POSITION = tkinter.Label(self.NEEDLE_Z_MOVE_FRAME, text="Z Value: ")
        self.Z_Label_POSITION.grid(row=0, column=7, sticky="nsew", padx=10)

        self.CONNECT_NEEDLE_DRIVER_BUTTON = tkinter.Button(self.NEEDLE_DRIVER_FRAME, text="Connect",
                                                           command=lambda: self.connect_needle_driver())
        self.CONNECT_NEEDLE_DRIVER_BUTTON.place(x=10, y=205, width=100)

        self.Needle_Driver = None

        # TODO: ADD A scrolled label with logging function?

        # -------Tkinter Treeview Elements-------
        self.treeviewframe = tkinter.LabelFrame(self, text="Treeview")
        self.treeviewframe.place(x=c.TREEVIEW_FRAME_X, y=c.TREEVIEW_FRAME_Y, width=c.TREEVIEW_WIDTH,
                                 height=c.TREEVIEW_HEIGHT)
        self.treeview = ttk.Treeview(self.treeviewframe)
        self.treeview['columns'] = ("Command", "X_Value", "Y_Value", "Z_Value")
        self.treeview.column("#0", width=0, stretch="NO")
        self.treeview.column("Command", anchor="w", width=120)
        self.treeview.column("X_Value", anchor="center", width=80)
        self.treeview.column("Y_Value", anchor="center", width=80)
        self.treeview.column("Z_Value", anchor="center", width=80)

        self.treeview.heading("#0", text="", anchor="w")
        self.treeview.heading("Command", text="Command", anchor="w")
        self.treeview.heading("X_Value", text="X_Value", anchor="w")
        self.treeview.heading("Y_Value", text="Y_Value", anchor="w")
        self.treeview.heading("Z_Value", text="Z_Value", anchor="w")

        self.treeview.grid(row=0, column=0, columnspan=4)

        # New Data entry
        self.entrybutton = tkinter.Button(self.treeviewframe, text="Insert", width=10, command=lambda: self.newentry())
        self.entrybutton.grid(row=4, column=0, pady=5)

        # Remove entry
        self.removentrybutton = tkinter.Button(self.treeviewframe, text="Remove", width=10,
                                               command=lambda: self.removentry())
        self.removentrybutton.grid(row=4, column=1)

        # moveup entry
        self.moveupentrybutton = tkinter.Button(self.treeviewframe, text="Move Up", width=10,
                                                command=lambda: self.moveuptree())
        self.moveupentrybutton.grid(row=4, column=2)

        # movedown entry
        self.movedownbutton = tkinter.Button(self.treeviewframe, text="Move Down", width=10,
                                             command=lambda: self.movedowntree())
        self.movedownbutton.grid(row=4, column=3)

        # # Import Excel file
        # self.filebutton = tkinter.Button(self.treeviewframe, text="Import", width=10, command=lambda: self.fileopen())
        # self.filebutton.grid(row=5, column=0)
        # Clear all in treeview
        self.clearallbutton = tkinter.Button(self.treeviewframe, text="Clear All", width=10,
                                             command=lambda: self.clearall())
        self.clearallbutton.grid(row=5, column=1)
        # Execute
        self.executetree = tkinter.Button(self.treeviewframe, text="Execute", width=24,
                                          command=lambda: self.executiontree())
        self.executetree.grid(row=5, column=2, columnspan=2)

        # Input new data field
        self.commandlabel = tkinter.Label(self.treeviewframe, text="Command")
        self.commandlabel.grid(row=1, column=0)

        self.treexlabel = tkinter.Label(self.treeviewframe, text="X_Value")
        self.treexlabel.grid(row=1, column=1)

        self.treeylabel = tkinter.Label(self.treeviewframe, text="Y_Value")
        self.treeylabel.grid(row=1, column=2)

        self.step = tkinter.Label(self.treeviewframe, text="Z_Value")
        self.step.grid(row=1, column=3)

        self.commandentry = tkinter.Entry(self.treeviewframe, width=15)
        self.commandentry.grid(row=2, column=0)

        self.treexentryx = tkinter.Entry(self.treeviewframe, width=15)
        self.treexentryx.grid(row=2, column=1)

        self.treeyentry = tkinter.Entry(self.treeviewframe, width=15)
        self.treeyentry.grid(row=2, column=2)

        self.stepentry = tkinter.Entry(self.treeviewframe, width=15)
        self.stepentry.grid(row=2, column=3)

        # ---------End of treeview  elements -------

        self.update_canvas()
        self.update_info_frame_label()
    def Update_Robot_Data(self):
        """Update_Robot_Data updates the register from the robot side to the computer side"""

        state = self.Robot.Update_Data()

        # self.TCP_Text_Variable = str(self.state.actual_TCP_pose)
        # self.after(self.delay, self.Update_Robot_Data())
        self.TCP_TEXT_VARIABLE.set(str(state.get("TCP_POS")))
        # print(state.actual_TCP_pose)
        self.INPUT_REGISTER00.set(state.get("input_double_register0"))
        self.INPUT_REGISTER01.set(state.get("input_double_register1"))
        self.INPUT_REGISTER02.set(state.get("input_double_register2"))
        self.INPUT_REGISTER03.set(state.get("input_double_register3"))
        self.INPUT_REGISTER04.set(state.get("input_double_register4"))
        self.INPUT_REGISTER05.set(state.get("input_double_register5"))

        # defaults back to MODE 0 after it receives that input_integer_register0 == 2 aka each execution of the program is completed
        if state.get("input_integer_register0") == 2:
            print("input reg == 2 ")
            self.Robot.watchdog.input_int_register_0 = 0
            self.Robot.con.send(self.Robot.watchdog)

        self.after(2, self.Update_Robot_Data)

    def update_info_frame_label(self):
        try:
            self.X_US_COORDINATES.set(self.main_image.X_US_coordinates)
            self.Y_US_COORDINATES.set(self.main_image.Y_US_coordinates)
        except Exception as error:
            print("No US distance data can be displayed", error)

        try:
            self.ALPHA.set(self.main_image.Alpha)
        except Exception as error:
            print("No alpha data can be displayed", error)
        try:
            self.OFFSET_X_DISTANCE.set(self.main_image.x_distance)
        except Exception as error:
            print("No x_distance_move data can be displayed",error)
        try:
            self.OFFSET_D_DISTANCE.set(self.main_image.d_distance)
        except Exception as error:
            print("No d_distance data can be displayed",error)
        try:
            self.MOVE_DISTANCE_ACTUATOR.set(self.main_image.actuator_move_value)
        except Exception as error:
            print("No actuator_move_value can be displayed", error)
        try:
            self.MOVE_UR_ROBOT_BY.set(self.main_image.robot_move_value)
        except Exception as error:
            print("No UR_move_value can be displayed",error)

        #temporary set.US_distance is used for pixel_distance for target
        try:
            self.X_US_SURFACE_TARGET_COORDINATES.set(self.main_image.distance_target_pixel)
        except Exception as error:
            print("No pixel distance between target and origin can be displayed", error)

        try:
            self.Y_US_SURFACE_TARGET_COORDINATES.set(self.main_image.distance_target_US)
        except Exception as error:
            print("No actual distance in m between target and origin can be displayed",error)

        self.after(self.delay, self.update_info_frame_label)


    def update_canvas(self):
        start_time = time.time()

        # if (self.main_image.clent.is_connected()) == False:
        #     print("CLIENT IS NOT CONNECTED")
        #     return

        # try:
        #     self.img = self.cont.show_original()
        #     # self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        #     self.img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.img))
        #     self.Canvas.create_image(0, 0, image=self.img, anchor="nw")
        #
        # except:
        #     print("No Image")
        #     pass

        # if self.US_image != None:
        #     # self.display = self.US_image.show_original_image()
        #     self.display = self.US_image.receive_image_message()
        #     self.display = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.display))
        #     self.Canvas.create_image(0, 0, image=self.display, anchor="nw")
        try:
            self.CheckCB()
        except:
            print("NONE OBJECT NO CB")

        try:
            self.main_image.show_live_image()
            self.display = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.main_image.labelled_img))
            self.Canvas.create_image(0, 0, image=self.display, anchor="nw")
        except Exception as error:
            print("No image can be displayed", error)

        # try:
        #     self.display = self.img.show_original_image()
        #     self.display = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.display))
        #     self.Canvas.create_image(0, 0, image=self.display, anchor="nw")
        #
        # except Exception as error:
        #     print("An error occurred:", error)  # An error occurred: name 'x' is not defined

        self.after(self.delay, self.update_canvas)

    def update_Needle_Driver_Data(self):
        try:
            self.Needle_Driver.read_values()
            "Updates Label of the X/Y/Z of the needle label"
            self.X_Label_POSITION["text"] = "X_Value: " + str(self.Needle_Driver.X_ND_Values)
            self.Y_Label_POSITION["text"] = "Y Value: " + str(self.Needle_Driver.Y_ND_Values)
            self.Z_Label_POSITION["text"] = "Z Value: " + str(self.Needle_Driver.Z_ND_Values)
        except Exception as error:
            print("ERROR!")
            print(error)
        self.after(500, self.update_Needle_Driver_Data)

    def freeze_frame(self, frame_number):
        if frame_number == 2:
            try:
                self.main_image.image_freeze_frame(2)
                if self.main_image.frame_two_freezed == True:
                    self.Image_Two_Screen_Freeze_Button.config(relief = 'sunken')
                    self.Image_Two_Screen_Freeze_Button.config(bg = 'spring green')
                else:
                    self.Image_Two_Screen_Freeze_Button.config(relief = 'raised')
                    self.Image_Two_Screen_Freeze_Button.config(bg = 'SystemButtonFace')
            except Exception as error:
                print("No image to freeze 02")

        elif frame_number == 4:
            try:
                self.main_image.image_freeze_frame(4)
                if self.main_image.frame_four_freezed == True:
                    self.Image_Four_Screen_Freeze_Button.config(relief = 'sunken')
                    self.Image_Four_Screen_Freeze_Button.config(bg = 'spring green')
                else:
                    self.Image_Four_Screen_Freeze_Button.config(relief = 'raised')
                    self.Image_Four_Screen_Freeze_Button.config(bg = 'SystemButtonFace')

            except Exception as error:
                print("No image to freeze 04")




    def Delete_Entry(self):
        self.commandentry.delete(0, 'end')
        self.treexentryx.delete(0, 'end')
        self.treeyentry.delete(0, 'end')
        self.stepentry.delete(0, 'end')

    def Populate_Field(self):
        # clear all
        self.treeview.delete(*self.treeview.get_children())

        # send the command to home position of the ND y-axis
        self.treeview.insert('', 'end', values=("ND_HOME_Y", 0.0, 0.0, 0.0))

        # send the command to home position of the ND z-axis
        self.treeview.insert('', 'end', values=("ND_HOME_Z", 0.0, 0.0, 0.0))

        # move the y-axis to the intended needle path
        self.treeview.insert('', 'end', values=("ND_MOVE_Y", 0.0, self.MOVE_DISTANCE_ACTUATOR.get(), 0.0))

        # send command to the UR to move up by a certain z (Mode1)
        self.treeview.insert('', 'end', values=("UR_MOVE_Z_UP", 0.0, 0.0, 0.001))

        # get the coordinates to move to in the US frame (Move relative,Mode2)
        self.treeview.insert('', 'end', values=("UR_MOVE_RELATIVE", self.MOVE_UR_ROBOT_BY.get(), 0.0, 0.0))

        # send the command to the UR to move to the US intended position by moving z down to the point(Mode3)
        self.treeview.insert('', 'end', values=("UR_MOVE_Z_DOWN", 0.0, 0.0, -0.001))

        # inject the needle by
        # send the commad to move Z needle down
        self.treeview.insert('', 'end', values=("ND_MOVE_Z", 0.0, 0.0, 0.0))

        # self.treeview.insert('',end, values= )

    def moveuptree(self):
        rows = self.treeview.selection()
        for row in rows:
            self.treeview.move(row, self.treeview.parent(row), self.treeview.index(row) - 1)

    def movedowntree(self):
        rows = self.treeview.selection()
        for row in reversed(rows):
            self.treeview.move(row, self.treeview.parent(row), self.treeview.index(row) + 1)

    def removentry(self):
        rows = self.treeview.selection()
        # print(rows)
        for row in rows:
            self.treeview.delete(row)

        # Open file function

    # def fileopen(self):
    #     filename = filedialog.askopenfilename(initialdir="C:/documents", title="Open file",
    #                                           filetype=(("xlsx files", "*.xlsx"), ("All Files", "*.*")))
    #     if filename:
    #         try:
    #             file = r"{}".format(filename)
    #             df = pd.read_excel(file)
    #             df = df.fillna("")
    #             df_rows = df.to_numpy().tolist()
    #         except ValueError:
    #             print("File could not be read")
    #         except FileNotFoundError:
    #             print("File could not be found")
    #     for row in df_rows:
    #         self.treeview.insert("", "end", values=row)
    #     # clear all from treeview

    def clearall(self):
        self.treeview.delete(*self.treeview.get_children())

        # add entry

    def newentry(self):
        if self.commandentry.get() == '' and self.treexentryx.get() == '' and self.treeyentry.get() == '' and self.stepentry.get() == '':
            print('nothing!')
            pass
        else:
            self.treeview.insert('', 'end', values=(
                self.commandentry.get(), self.treexentryx.get(), self.treeyentry.get(), self.stepentry.get()))
            self.commandentry.delete(0, 'end')
            self.treexentryx.delete(0, 'end')
            self.treeyentry.delete(0, 'end')
            self.stepentry.delete(0, 'end')

    def executiontree(self):
        self.executelist = []
        for items in self.treeview.get_children():
            # print(items)
            item_text = self.treeview.item(items)
            item_text = item_text.get('values')
            command_dictionary = {"iid": items, "command": item_text}
            self.executelist.append(command_dictionary)

        command = threading.Thread(target=self.executionfunction, args=(self.executelist,))
        command.start()
        # print(self.executelist)

    # KIV? Seems to work without threading now...
    # def thread_wait(self,duration):
    #     time.sleep(duration)
    #     self.Robot_Change_Mode(1)
    #     print("MOVE UP")
    def executionfunction(self, instructions):
        for commands in instructions:
            self.treeview.selection_set(commands.get("iid"))
            try:
                valx = float(commands.get("command")[1])
                print(valx)
            except Exception as error:
                print("x value invalid!" + str(error))
                pass
            try:
                valy = float(commands.get("command")[2])
                print(valy)
            except Exception as error:
                print("y value invalid!" + str(error))
            try:
                valz = float(commands.get("command")[3])
                print(valz)
            except Exception as error:
                print("z value invalid!" + str(error))
                pass

            if commands.get("command")[0] == "ND_HOME_X":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("X", "START")
                    self.Needle_Driver.wait_for_idle()
                    # time.sleep(10)
                except Exception as error:
                    print("CANNOT HOME X_NEEDLE_DRIVER" + str(error))
            elif commands.get("command")[0] == "ND_HOME_Y":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Y", "START")
                    self.Needle_Driver.wait_for_idle()

                    # self.Needle_Driver.send_needle_driver_home_command("Y", "STOP")

                except Exception as error:
                    print("CANNOT HOME Y_NEEDLE_DRIVER" + str(error))
            elif commands.get("command")[0] == "ND_HOME_Z":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Z", "START")
                    self.Needle_Driver.wait_for_idle()

                    # self.Needle_Driver.send_needle_driver_home_command("Z", "STOP")

                except Exception as error:
                    print("CANNOT HOME Z_NEEDLE_DRIVER" + str(error))

            elif commands.get("command")[0] == "ND_MOVE_X":
                try:
                    self.Needle_Driver.z_move_command(valx, "START")
                    self.Needle_Driver.wait_for_idle()
                except:
                    print("CANNOT MOVE TO REQUIRED X VALUE")

            elif commands.get("command")[0] == "ND_MOVE_Y":
                try:
                    self.Needle_Driver.y_move_command(valy,"START")
                    self.Needle_Driver.wait_for_idle()
                    # time.sleep(10)
                except Exception as error:
                    print("CANNOT MOVE TO REQUIRED Y VALUE" + str(error))
            elif commands.get("command")[0] == "ND_MOVE_Z":
                # currently using the hacky way of jogging Z motor instead of positioning
                try:
                    self.Needle_Driver.z_move_command(valz, "START")
                    self.Needle_Driver.wait_for_idle()
                except Exception as error:
                    print("CANNOT MOVE TO REQUIRED Z VALUE" + str(error))

            elif commands.get("command")[0] == "UR_MOVE_Z_UP":
                self.Robot_Change_Mode(1)
                # Mode 1 is move UR robot up z axis by 10mm
                # thread_1 = threading.Thread(target=self.thread_wait, args=(10,))
                # thread_1.start()
                time.sleep(5)

            elif commands.get("command")[0] == "UR_MOVE_RELATIVE":
                move_value_by_in_mm = float(self.MOVE_UR_ROBOT_BY.get()/1000)
                move_value_by_in_mm = round(move_value_by_in_mm,6)
                move_value_by_in_mm = -move_value_by_in_mm
                registers = [0, move_value_by_in_mm, 0, 0, 0, 0]
                Result = self.Robot.list_to_setp(registers)
                self.Robot.con.send(Result)
                self.Robot_Change_Mode(2)
                time.sleep(5)

            elif commands.get("command")[0] == "UR_MOVE_Z_DOWN":
                # Mode 3 on Robot is the move down until detect force
                self.Robot_Change_Mode(3)
                time.sleep(5)

            # thread_1 = threading.Thread(target=self.thread_wait, args=(30,))
            # thread_1.start()
            #     try:
            #         self.Robot_Change_Mode(self, 1)
            #     except:
            #         print("FAILED TO CHANGE MODE TO 1")
            # elif commands.get("command")[0] == "UR_MOVE_X":
            #     try:
            #         self.Robot_Change_Mode(self, 2)
            #     except:
            #         print("FAILED TO CHANGE MODE TO 2")


            print("NEXT COMMAND")

    def Select_Origin_Button_Function(self):
        try:
            self.main_image.select_origin()
        except:
            print("ERROR")
            pass

    def Draw_Needle_Button_Function(self):
        try:
            self.main_image.draw_needle_line()
        except:
            print("ERROR")
            pass

    def Select_Target(self):
        try:
            self.main_image.select_target()
        except:
            print("ERROR")
            pass

    def connection_igtl_client(self):
        if not self.igtl_initialised:
            self.main_image = US_Screen.US_Image.US_IMAGE()
            self.igtl_initialised = True
        else:

            self.main_image.connect_igtl_client()

    def CheckCB(self):
        """Function to check tkinter_CB elements updates main_image attributes after checked"""
        if self.Show_Origin_CB_Var.get() == 1:
            self.main_image.show_origin_CB = True
        else:
            self.main_image.show_origin_CB = False

        if self.Show_Needle_CB_Line_Var.get() == 1:
            self.main_image.show_needle_line_CB = True
        else:
            self.main_image.show_needle_line_CB = False

        if self.Show_Projected_Line_CB_Var.get() == 1:
            self.main_image.show_projected_needle_line_CB = True
        else:
            self.main_image.show_projected_needle_line_CB = False

        if self.Show_US_Coord_CB_Var.get() == 1:
            self.main_image.show_US_coordinate_CB = True
        else:
            self.main_image.show_US_coordinate_CB = False

        if self.Show_Target_CB_Var.get() == 1:
            self.main_image.show_target_CB = True
        else:
            self.main_image.show_target_CB = False

        if self.Show_Stacked_Images_CB_Var.get() == 1:
            self.main_image.show_stacked_images_CB = True
        else:
            self.main_image.show_stacked_images_CB = False
    def needle_driver_toggle_button(self, key):
        """Function callback when button "X+,X-,Y+,Y-,Z+,Z-"is pressed. Configure buttons"""

        if key == "X+":
            if self.X_PLUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("X+", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))

                self.X_PLUS_TOGGLE_BUTTON.config(relief='sunken')
                self.X_PLUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("X+", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_PLUS_TOGGLE_BUTTON.config(relief="raised")
                self.X_PLUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')
        if key == "X-":
            if self.X_MINUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("X-", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))

                self.X_MINUS_TOGGLE_BUTTON.config(relief='sunken')
                self.X_MINUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("X-", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_MINUS_TOGGLE_BUTTON.config(relief="raised")
                self.X_MINUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')

        if key == "Y+":
            if self.Y_PLUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Y+", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_PLUS_TOGGLE_BUTTON.config(relief='sunken')
                self.Y_PLUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Y+", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_PLUS_TOGGLE_BUTTON.config(relief="raised")
                self.Y_PLUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')
        if key == "Y-":
            if self.Y_MINUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Y-", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_MINUS_TOGGLE_BUTTON.config(relief='sunken')
                self.Y_MINUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Y-", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_MINUS_TOGGLE_BUTTON.config(relief="raised")
                self.Y_MINUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')
        if key == "Z+":
            if self.Z_PLUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Z+", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_PLUS_TOGGLE_BUTTON.config(relief='sunken')
                self.Z_PLUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Z+", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_PLUS_TOGGLE_BUTTON.config(relief="raised")
                self.Z_PLUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')
        if key == "Z-":
            if self.Z_MINUS_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Z-", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_MINUS_TOGGLE_BUTTON.config(relief='sunken')
                self.Z_MINUS_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_toggle_command("Z-", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_MINUS_TOGGLE_BUTTON.config(relief="raised")
                self.Z_MINUS_TOGGLE_BUTTON.config(bg='SystemButtonFace')

    def needle_driver_home_button(self, axis):
        if axis == "X":
            if self.X_HOME_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("X", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_HOME_TOGGLE_BUTTON.config(relief='sunken')
                self.X_HOME_TOGGLE_BUTTON.config(bg='spring green')
                # TODO: ADD RESPONSE FEEDBACK WHEN HOME, CHANGE RELIEF AND COLOR BACK TO RAISED AND OG

            else:
                try:
                    self.Needle_Driver.send_needle_driver_home_command("X", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_HOME_TOGGLE_BUTTON.config(relief="raised")
                self.X_HOME_TOGGLE_BUTTON.config(bg='SystemButtonFace')

        if axis == "Y":
            if self.Y_HOME_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Y", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_HOME_TOGGLE_BUTTON.config(relief='sunken')
                self.Y_HOME_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Y", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_HOME_TOGGLE_BUTTON.config(relief="raised")
                self.Y_HOME_TOGGLE_BUTTON.config(bg='SystemButtonFace')

        if axis == "Z":
            if self.Z_HOME_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Z", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_HOME_TOGGLE_BUTTON.config(relief='sunken')
                self.Z_HOME_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_home_command("Z", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_HOME_TOGGLE_BUTTON.config(relief="raised")
                self.Z_HOME_TOGGLE_BUTTON.config(bg='SystemButtonFace')

    def needle_driver_stop_button(self, axis):
        if axis == "X":
            try:
                self.Needle_Driver.send_needle_driver_stop_command("X")
            except AttributeError as e:
                print("ERROR: " + str(e))

        if axis == "Y":
            try:
                self.Needle_Driver.send_needle_driver_stop_command("Y")
            except AttributeError as e:
                print("ERROR: " + str(e))

        if axis == "Z":
            try:
                self.Needle_Driver.send_needle_driver_stop_command("Z")
            except AttributeError as e:
                print("ERROR: " + str(e))

    def needle_driver_reset_button(self, axis):
        if axis == "X":
            if self.X_RESET_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("X", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_RESET_TOGGLE_BUTTON.config(relief='sunken')
                self.X_RESET_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("X", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.X_RESET_TOGGLE_BUTTON.config(relief="raised")
                self.X_RESET_TOGGLE_BUTTON.config(bg='SystemButtonFace')

        if axis == "Y":
            if self.Y_RESET_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("Y", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_RESET_TOGGLE_BUTTON.config(relief='sunken')
                self.Y_RESET_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("Y", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Y_RESET_TOGGLE_BUTTON.config(relief="raised")
                self.Y_RESET_TOGGLE_BUTTON.config(bg='SystemButtonFace')

        if axis == "Z":
            if self.Z_RESET_TOGGLE_BUTTON["relief"] == "raised":
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("Z", "START")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_RESET_TOGGLE_BUTTON.config(relief='sunken')
                self.Z_RESET_TOGGLE_BUTTON.config(bg='spring green')
            else:
                try:
                    self.Needle_Driver.send_needle_driver_reset_command("Z", "STOP")
                except AttributeError as e:
                    print("ERROR: " + str(e))
                self.Z_RESET_TOGGLE_BUTTON.config(relief="raised")
                self.Z_RESET_TOGGLE_BUTTON.config(bg='SystemButtonFace')

    def needle_driver_move_button(self, axis):
        if axis == "X":
            try:
                value = self.X_NEEDLE_ENTRY_BOX.get()
                self.Needle_Driver.x_move_command(value,"START")
            except AttributeError as e:
                print("ERROR: " + str(e))
        if axis == "Y":
            try:
                value = self.Y_NEEDLE_ENTRY_BOX.get()
                self.Needle_Driver.y_move_command(value,"START")
            except AttributeError as e:
                print("ERROR: " + str(e))
        if axis == "Z":
            try:
                value = self.Z_NEEDLE_ENTRY_BOX.get()
                self.Needle_Driver.z_move_command(value,"START")
            except AttributeError as e:
                print("ERROR: " + str(e))

    def connect_needle_driver(self):
        try:
            self.Needle_Driver = ND.NeedleDriverController()
            self.update_Needle_Driver_Data()

        except:
            print("ERORR. Needle Driver not connected")

    def convert_pixel_to_US_coord(self):
        try:
            self.main_image.mm_per_pixel = float(self.MILIMTR_PER_PIXEL.get())
            self.main_image.Convert_Pixel_to_US_Coord()
        except AttributeError as e:
            print("ERROR: " + str(e))

    def Robot_Connect_Button(self):
        Robot_IP = self.IP_Text_Variable.get()
        print(Robot_IP)
        self.Robot = UR_Robot.UR_ROBOT.UR_10E(Robot_IP)

        self.Robot.watchdog.input_int_register_0 = 0
        self.Robot.con.send(self.Robot.watchdog)

        self.Update_Robot_Data()
        # print("CONNECTED UR_ROBOT")

    def Robot_Change_Mode(self, int_var):
        # int_var = self.UR_MODE.get()
        self.Robot.watchdog.input_int_register_0 = int_var
        self.Robot.con.send(self.Robot.watchdog)

    def Robot_Send_Output(self):
        reg0 = self.OUTPUT_DB_REG0.get()
        reg1 = self.OUTPUT_DB_REG1.get()
        reg2 = self.OUTPUT_DB_REG2.get()
        reg3 = self.OUTPUT_DB_REG3.get()
        reg4 = self.OUTPUT_DB_REG4.get()
        reg5 = self.OUTPUT_DB_REG5.get()

        LIST = [reg0, reg1, reg2, reg3, reg4, reg5]
        print(LIST)
        Result = self.Robot.list_to_setp(LIST)
        self.Robot.con.send(Result)
        print("send successfully")
