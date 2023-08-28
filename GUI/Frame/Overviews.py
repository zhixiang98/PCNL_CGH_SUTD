import tkinter
import GUI.Frame.constants as c
import UR_Robot
import cv2
import PIL


class Overview(tkinter.Frame):

    def __init__(self, parent, cont):
        tkinter.Frame.__init__(self, parent)
        self.cont = cont
        self.delay = c.REFRESH_DELAY
        self.img = None

        self.origin_selected = False  # Bool False if origin is not selected yet
        self.target_selected = False  # Bool_False if target is not selected yet
        self.needle_line_drawn = False  # Bool_False if needle line is not drawn yet

        # --- Tkinter Variables ---
        # """Tkinter Variables will be in CAPs"""
        self.X_US_COORDINATES, self.Y_US_COORDINATES = tkinter.DoubleVar(), tkinter.DoubleVar
        self.THETA = tkinter.DoubleVar()

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
        self.Canvas = tkinter.Canvas(self, bg=c.CANVAS_BG, height=c.CANVAS_HEIGHT, width=c.CANVAS_WIDTH, bd=c.CANVAS_BD,
                                     highlightthickness=c.CANVAS_HIGHLIGHT, relief=c.CANVAS_RELIEF)
        self.Canvas.grid(row = c.CANVAS_ROW , column = c.CANVAS_COLUMN)

        self.Image_Setting_Label_Frame = tkinter.LabelFrame(self, text = 'Image Settings')
        self.Image_Setting_Label_Frame.place(x=c.IMAGE_SETTING_LBL_FRAME_X, y = c.IMAGE_SETTING_LBL_FRAME_Y, width =c.IMAGE_SETTING_LBL_FRAME_WIDTH, height = c.IMAGE_SETTING_LBL_FRAME_HEIGHT)

        # -- Image_Setting_Label_Frame---
        self.Select_Origin_Button = tkinter.Button(self.Image_Setting_Label_Frame, text =c.ORIGIN_BUTTON_TEXT,width = c.BUTTON_WIDTH, command = lambda: self.Select_Origin() )
        self.Select_Origin_Button.grid(row = c.ORIGIN_BUTTON_ROW, column = c.ORIGIN_BUTTON_COLUMN, padx = c.PADX, pady= c.PADY)

        self.Select_Target_Button = tkinter.Button(self.Image_Setting_Label_Frame, text = c.SELECT_TARGET_BUTTON_TEXT,width =c.BUTTON_WIDTH, command=lambda:self.Select_Target())
        self.Select_Target_Button.grid(row = c.SELECT_TARGET_BUTTON_ROW, column = c.SELECT_TARGET_BUTTON_COLUMN, padx = c.PADX, pady = c.PADY)

        self.Theta_Button = tkinter.Button(self.Image_Setting_Label_Frame, text = c.THETA_BUTTON_TEXT, command = lambda:self.calculate_target_ange(), width = c.BUTTON_WIDTH)
        self.Theta_Button.grid(row = c.SELECT_TARGET_BUTTON_ROW, column = c.SELECT_TARGET_BUTTON_COLUMN, padx =c.PADX, pady = c.PADY)

        self.Draw_Needle_Button = tkinter.Button(self.Image_Setting_Label_Frame, text = c.DRAW_NEEDLE_BUTTON_TEXT, command = lambda:self.draw_needle_line(), width =c.BUTTON_WIDTH)
        self.Draw_Needle_Button.grid(row = c.DRAW_NEEDLE_BUTTON_ROW, column = c.DRAW_NEEDLE_BUTTON_COLUMN, padx = c.PADX, pady = c.PADY)

        self.Convert_Pixel2Coordinates_Button = tkinter.Button(self.Image_Setting_Label_Frame, text = c.CONVERT_PIXEL2COORDINATES_TEXT, command=lambda:self.convert_pixel_to_US_coord(), width = c.BUTTON_WIDTH)
        self.Convert_Pixel2Coordinates_Button.grid(row = c.CONVERT_PIXEL2COORDINATES_ROW, column = c.CONVERT_PIXEL2COORDINATES_COLUMN, padx = c.PADX, pady = c.PADY)

        # --- CB tkinter variables---
        self.Show_Origin_CB_Var = tkinter.IntVar()
        self.Show_Needle_CB_Line_Var = tkinter.IntVar()
        self.Show_Target_CB_Var = tkinter.IntVar()
        self.Show_US_Coord_CB_Var = tkinter.IntVar()
        self.Show_Projected_Line_CB_Var = tkinter.IntVar()

        # --- CB tkinter ----
        self.show_projected_line_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_projected_line",
                                                  variable=self.Show_Projected_Line_CB_Var, onvalue=1, offvalue=0)
        self.show_projected_line_CB.grid(row=2, column=4, padx=20, columnspan=2, sticky="w")

        self.show_origin_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_origin",
                                          variable=self.Show_Origin_CB_Var, onvalue=1,
                                          offvalue=0)
        self.show_origin_CB.grid(row=2, column=0, padx=20)

        self.show_needle_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_needle",
                                          variable=self.Show_Needle_CB_Line_Var,
                                          onvalue=1, offvalue=0)
        self.show_needle_CB.grid(row=2, column=2, padx=20)

        self.show_target_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_target",
                                          variable=self.Show_Target_CB_Var,
                                          onvalue=1, offvalue=0)
        self.show_target_CB.grid(row=2, column=1, padx=20)

        self.show_US_Coord_CB = tkinter.Checkbutton(self.Image_Setting_Label_Frame, text="show_coordinates",
                                            variable=self.Show_US_Coord_CB_Var,
                                            onvalue=1, offvalue=0)
        self.show_US_Coord_CB.grid(row=2, column=3, padx=20)

        # --------US_INFO_LABEL_FRAME--------------

        self.US_INFO_LABEL_FRAME = tkinter.LabelFrame(self, text="Ultrasound Information")
        self.US_INFO_LABEL_FRAME.place(x=1580, y=0, width=220, height=300)

        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.X_US_COORDINATES).grid(row=1, column=2)
        tkinter.Label(self.US_INFO_LABEL_FRAME, text="X US Coordinates: ").grid(row=1, column=1)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="Y US Coordinates: ").grid(row=2, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.Y_US_COORDINATES).grid(row=2, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="Theta: ").grid(row=4, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.THETA).grid(row=4, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="X Surface Coordinates: ").grid(row=5, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.X_US_SURFACE_TARGET_COORDINATES).grid(row=5, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="Y Surface Coordinates: ").grid(row=6, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.Y_US_SURFACE_TARGET_COORDINATES).grid(row=6, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="offset x distance: ").grid(row=7, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.OFFSET_X_DISTANCE).grid(row=7, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="offset d distance: ").grid(row=8, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.OFFSET_D_DISTANCE).grid(row=8, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="move actuator distance: ").grid(row=9, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.MOVE_DISTANCE_ACTUATOR).grid(row=9, column=2)

        tkinter.Label(self.US_INFO_LABEL_FRAME, text="move UR Robot by: ").grid(row=10, column=1)
        tkinter.Label(self.US_INFO_LABEL_FRAME, textvariable=self.MOVE_UR_ROBOT_BY).grid(row=10, column=2)

        #---Tkinter Variables ---
        self.X_DISTANCE_TO_MOVE = tkinter.DoubleVar()
        self.TCP_TEXT_VARIABLE = tkinter.StringVar()
        self.INPUT_REGISTER00 = tkinter.DoubleVar()
        self.INPUT_REGISTER01 = tkinter.DoubleVar()
        self.INPUT_REGISTER02 = tkinter.DoubleVar()
        self.INPUT_REGISTER03 = tkinter.DoubleVar()
        self.INPUT_REGISTER04 = tkinter.DoubleVar()
        self.INPUT_REGISTER05 = tkinter.DoubleVar()


        self.update_canvas()

    def update_canvas(self):
        try:
            self.img =self.cont.show_original()
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            # print(self.img.shape)
            self.img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.img))
            self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        except:
            pass
        self.after(c.REFRESH_DELAY,self.update_canvas)


