import pyigtl
import time
import numpy as np
from PIL import Image
import cv2
import copy
import math


class US_IMAGE():
    def __init__(self,igtl_status):
        # ---Pixel Coordinates---
        """
        Origin_Pixel_X, Origin_Pixel_Y are pixel coordinates  of the clicked origin from self.select_origin(). Measured from the image using CV2 coordinates
        Target_Pixel_X, Target_Pixel_Y are pixel coordinates measured from the image using CV2 coordinates. TODO: Not currently implemented
        Target_Surface_X, Target_Pixel_Y are pixel coordinated measured from the image. It is the intersection of the interpolation of drawn-needle-line and the horizontal line drawn from origin

        Needle_Start_Pixel_X, Needle_Start_Pixel_Y are pixel coordinates of the start point of the clicked points from draw_needle_line(). Measured from the image using CV2 coordinates
        Needle_End_Pixel_X, Needle_End_Pixel_Y are pixel coordinates of the end point of the clicked points from draw_needle_line(). Measured from the image using CV2 coordinates

        Projected_Needle_Start_Pixel_X, Needle_Start_Pixel_Y are pixel coordinates of the projected start point of the Needle path after robot has moved Measured from the image using CV2 coordinates
        Projected_Needle_End_Pixel_X, Needle_End_Pixel_Y are pixel coordinates of the projected end point of the Needle path after robot has moved. Measured from the image using CV2 coordinates
        TODO: Not implemented yet


        """
        self.Origin_Pixel_X, self.Origin_Pixel_Y = 0, 0
        self.Target_Pixel_X, self.Target_Pixel_Y = 0, 0
        self.Surface_Pixel_X, self.Surface_Pixel_Y = 0, 0

        self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = 0, 0
        self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = 0, 0

        self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y = 0, 0
        self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y = 0, 0

        self.Intended_Needle_Start_Pixel_X, self.Intended_Needle_Start_Pixel_Y = 0, 0
        self.Intended_Needle_End_Pixel_X, self.Intended_Needle_End_Pixel_Y = 0, 0


        # ---Ultrasound Coordinates---
        """
        Ultrasound Coordinates are ALL measured from the center contact of the US probe
        To be in the units of :  < mm>
        Distance between points derived from multiplying distance/pixel <mm>/pixel (get from US machine) * pixels between points
        
        Origin_US_X, Origin_US_Y are the ultrasound coordinates. They are measured wrt from origin of the US (center of the US probe)
        Needle_Start_US_X, Needle_Start_US_Y are the needle in terms of the ultrasound coordinates. 
        Needle_Stop_US_X, Needle_Start_US_Y are the needle in terms of the ultrasound coordinates. 

        """

        self.Origin_US_X, self.Origin_US_Y = 0, 0
        self.Needle_Start_US_X, self.Needle_Start_US_Y = 0, 0
        self.Needle_End_US_X, self.Needle_End_US_Y = 0, 0
        self.Surface_US_X, self.Surface_US_Y = 0, 0

        self.Projected_Needle_Start_US_X, self.Projected_Needle_Start_US_Y = 0, 0
        self.Projected_Needle_End_US_X, self.Projected_Needle_End_US_Y = 0, 0

        self.X_US_coordinates, self.Y_US_coordinates = 0, 0  # currently not in used. to be used for target/ mouse selection to show distance between point and origin

        self.Intended_Needle_Start_US_X, self.Intended_Needle_Start_US_Y = 0, 0
        self.Intended_Needle_End_US_X, self.Intended_Needle_End_US_Y = 0, 0

        # --- Important values---
        """
        Theta is the angle measured from the drawn needle line with the vertical axis
        Alpha is the angle actual angle made from the inserted needle with the vertical axis
        x_distance is the fixed distance measured from the fixed point of the actuator to the needle
        d_distance is the horizontal distance measured from the probe to the needle 
        """
        self.igtl_available = igtl_status
        self.Theta = 0
        self.Alpha = 0
        self.Alpha_in_radians = self.Alpha / 180 * math.pi
        self.x_distance = 0  # x_distance is from the fixed point of actuator to needle
        self.d_distance = 0  # d_distance is the horizontal distance from the probe to the needle
        self.actuator_move_value = 0  # value to input to the needle driver
        self.robot_move_value = 0

        self.gradient = 0
        self.intersect = 0

        self.mm_per_pixel = 0  # mm per pixel provided by the US
        self.RCM_US_distance_x_mm = 0
        self.RCM_US_distance_y_mm = 0

        # ---- igtl configuration ---------
        """
        host depends on the IP address of the US machine. Ideally try to make this same as robot/ FT-Sensor
        port also depends on the dedicated port of the US machine
        """
        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)
        if self.igtl_available == True:

            self.client = pyigtl.OpenIGTLinkClient(host="192.168.1.49", port=23338)

        self.img_source_directory = None  # location for placeholder image

        # ----- image resolution received from the message. Resolution of the US machine (1432 x 740)
        self.imageSizeX = 1432
        self.imageSizeY = 740

        # --- Images for display ----
        """
        images in the formate of np nd_array to be used and passed on to the Overview
        all the image data should be named in the format of img
        
        self.img: main live time image that is displayed on the UI
        self.select_origin: image data of the drawn origin point of the US image
        self.cache1img: image data of the cache image of the drawn select_origin image
        self.cache2img: image data of the cache image of the drawn needle_line image
        
        """
        self.img = None  # live time image that is shown on the UI, can be stacked or single parse to Overviews
        self.select_origin_img = None  # select origin image
        self.cache1img = None  # image that is "cleared" to be used for the select_origin function
        self.cache2img = None  # image that is "cleared" to be used for the draw_needle_line function
        self.cache3img = None  # image that is "cleared" to be used for the select_target function
        self.labelled_img = None  # img that is finally displayed and pass to update canvas
        self.select_target_img = None

        self.single_img = None
        self.stacked_img = None

        self.freezed_image_two = None
        self.freezed_image_four = None

        # ----Boolean variables for origin button clicked------
        """
        Boolean variables that help to navigate the logic of the select_origin() and draw_needle_line()
        
        self.stacked_images_selected: False -> only the single live US will be shown, True -> stacked image of 2x2 will be shown
        """

        self.origin_selected = False
        self.draw_needle_line_selected = False
        self.target_selected = False
        self.stacked_images_selected = False
        self.draw_RCM_01_bool = False  #Iniialise draw_RCM_01_line
        self.draw_RCM_02_bool = False #Initialise draw RCM_02_line

        # -----CheckBoxes-----------
        self.show_origin_CB = False
        self.show_needle_line_CB = False
        self.show_projected_needle_line_CB = False
        self.show_US_coordinate_CB = False
        self.show_target_CB = False
        self.show_stacked_images_CB = False
        self.show_intended_line_CB = False
        self.show_RCM_CB = False

        self.frame_two_freezed = False
        self.frame_four_freezed = False

        self.frame_two_freezed_captured = False
        self.frame_four_freezed_captured = False

        # ---- for image detection/ best fit line-----
        self.show_image_detection_window = False
        self.show_image_detection_controller_window = False
        self.initialise_canvas = False
        self.initialState = None
        self.blank_canvas = None
        self.image_detection_coord_list = []
        self.imgStack = None
        self.edited_frame = None

        self.error_correction_value = None
        self.depth = None
        self.depth_lookup_dictionary = {9: 69, 10: 63, 11: 59, 12: 54, 13: 51, 14: 47, 15: 45, 16: 42, 17: 40, 18: 38,
                                        19: 36, 20: 34}
        self.superimpose_img = None
        self.kill_image_detection_window = False
        self.kill_image_detection_controller_window = False
        self.coord_list = []
        self.curr_x, self.curr_y = 0, 0
        self.prev_x, self.prev_y = 0, 0
        self.tol_x = 20
        self.tol_y = 20
        self.initialise = False

        self.draw_RCM01_img = None
        self.draw_RCM02_img = None
        self.cache4_img = None #draw RCM_cache_img
        self.cache5_img = None

        self.RCM_01_START_PIXEL_X, self.RCM_01_START_PIXEL_Y = 0,0
        self.RCM_01_END_PIXEL_X, self.RCM_01_END_PIXEL_Y = 0, 0
        self.RCM_02_START_PIXEL_X, self.RCM_02_START_PIXEL_Y = 0, 0
        self.RCM_02_END_PIXEL_X, self.RCM_02_END_PIXEL_Y = 0, 0

        self.gradient_RCM_01 = 0
        self.gradient_RCM_02 = 0

        self.intersect_RCM_01 = 0
        self.intersect_RCM_02 = 0

        self.RCM_PIXEL_X = 0
        self.RCM_PIXEL_Y = 0

        self.Overwrite_RCM_X_Entry_Value = 0
        self.Overwrite_RCM_Y_Entry_Value = 0

        self.box = None
        self.box_projected = None
    def calculateBestFitLine(self, vx, vy, x0, y0):
        """Return the best fit line, value in the terms of tupple (x_pt1, y_pt1), (x_pt2, y_pt2)"""
        x_pt1 = 0
        y_pt1 = int(((vy * x0 - vx * y0) - vy * x_pt1) / -vx)

        y_pt2 = 0
        x_pt2 = int(((vy * x0 - vx * y0) + vx * y_pt2) / vy)

        return (x_pt1, y_pt1), (x_pt2, y_pt2)

    def stackImages(self, scale, imgArray):
        """stackImages function allows for multiple image array to be displayed side by side. In a row x column square grid

         Parameters
         ----------
         scale: the scale to bring image down. 0<= scale <= 1
         imgArray: Image array in the format of tuple of list. e.g. ([img1,img2],[img3,img4])

         returns a numpy nd array of an image

         Raises
         ---------
         None
         """

        rows = len(imgArray)
        cols = len(imgArray[0])
        rowsAvailable = isinstance(imgArray[0], list)
        width = imgArray[0][0].shape[1]
        height = imgArray[0][0].shape[0]
        if rowsAvailable:
            for x in range(0, rows):
                for y in range(0, cols):
                    if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                    else:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                                    None, scale, scale)
                    if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
            imageBlank = np.zeros((height, width, 3), np.uint8)
            hor = [imageBlank] * rows
            hor_con = [imageBlank] * rows
            for x in range(0, rows):
                hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
        else:
            for x in range(0, rows):
                if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                else:
                    imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale,
                                             scale)
                if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
            hor = np.hstack(imgArray)
            ver = hor
        return ver

    def show_live_image_stacked(self, img1, img2, img3, img4):
        """Shows the stacked live image of 2x2 image arrays on the main UI.Update the attribute of self.img

         Parameters
         ----------
         img1: np ndarray
         img2: np ndarray
         img3: np ndarray
         img4: np ndarray

         Raises
         ------

         """
        self.stacked_img = self.stackImages(0.5, ([img1, img2], [img3, img4]))
        return self.stacked_img

    def connect_igtl_client(self):
        """Reconnects to IGT client. Print "RECONNECTED_CLIENT upon success

        Parameters
        -----
        none currently #TODO create a text field for different host and port number

        Raises
        -------

        """
        # Used for igl communication
        # self.client.stop()  # stop connection first
        if self.igtl_available == True:
            print("RECONNECTED_CLIENT")
        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)
            self.client = pyigtl.OpenIGTLinkClient(host="192.168.1.49", port=23338)
        else:
            pass

    def receive_image_message(self):
        """Receives message from server. Currently only receiving IMAGE messages

        Parameters
        ----------
        none currently """
        if self.igtl_available == True:

            self.message = self.client.wait_for_message(device_name="USImage", timeout=5.0)
        #
        # # used for igtl settings with US from CreativeMed
            self.img = self.message.image
            self.single_img = np.squeeze(self.img.reshape(1, self.imageSizeY, self.imageSizeX).transpose(0, 1, 2))
            self.single_img = np.asarray(self.single_img)
            self.img = np.asarray(self.single_img)

        # self.img = Image.open("GUI/sample_image01.png").convert("RGB")
        #
        # self.img = Image.open("../GUI/sample_image01.png").convert("RGB")

        # self.img = Image.open("../Img_source_four/Depth13cm.png")
        else:
            self.img = Image.open(self.img_source_directory)
            self.img = self.img.convert("RGB")
            self.img = np.asarray(self.img)

        # uncomment this for opencv server testing
        #     self.img = np.array(self.img)

    def show_live_image(self, img1=None, img2=None, img3=None, img4=None):
        """
        Parse self.receive_image_message() that updates self.img
        Display a single live image of the Ultra Sound screen.
        Display different images based on the different CB
        """
        self.receive_image_message()

        # #used for igtl settings with US from CreativeMed
        # self.receive_image_message()
        # if not self.stacked_images_selected:
        #     self.img = self.single_img
        # else:
        #     self.show_live_image_stacked(img1, img2, img3, img4)
        #     self.img = self.stacked_img
        #

        # placeholder image

        self.labelled_img = copy.deepcopy(self.img)

        if self.show_origin_CB == True:
            cv2.circle(self.labelled_img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
            cv2.line(self.labelled_img, (0, self.Origin_Pixel_Y), (2000, self.Origin_Pixel_Y), (255, 255, 255), 3)

        if self.show_needle_line_CB == True:
            cv2.line(self.labelled_img, (self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y),
                     (self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y), (255, 255, 255), 3)
            cv2.drawContours(self.labelled_img,[self.box],0,(255,255,255),2)

        if self.show_projected_needle_line_CB == True:
            # print("projected need pts are:")
            # print(self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_End_Pixel_X)
            cv2.line(self.labelled_img, (self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y),
                     (self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y), (255, 255, 0), 3)
            hypo_length_projected = int(math.sqrt((self.Projected_Needle_End_Pixel_X - self.Projected_Needle_Start_Pixel_X) ** 2 + (
                        self.Projected_Needle_End_Pixel_Y - self.Projected_Needle_Start_Pixel_Y) ** 2))
            rotation_rectangle = (((self.Projected_Needle_End_Pixel_X + self.Projected_Needle_Start_Pixel_X) / 2,
                                   (self.Projected_Needle_End_Pixel_Y + self.Projected_Needle_Start_Pixel_Y) / 2),
                                  (int(9 / self.mm_per_pixel), hypo_length_projected), self.Alpha)
            self.box_projected = cv2.boxPoints(rotation_rectangle)
            self.box_projected = np.int0(self.box_projected)
            cv2.drawContours(self.labelled_img,[self.box_projected],0,(255,255,255),2)


        if self.show_intended_line_CB == True:
            cv2.line(self.labelled_img, (self.Intended_Needle_Start_Pixel_X, self.Intended_Needle_Start_Pixel_Y),
                     (self.Intended_Needle_End_Pixel_X, self.Intended_Needle_End_Pixel_Y), (255, 0, 255), 3)


        if self.show_target_CB == True:
            cv2.circle(self.labelled_img, (self.Target_Pixel_X, self.Target_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
        if self.show_US_coordinate_CB == True:
            cv2.putText(self.labelled_img, '{}'.format((self.Target_Pixel_X, self.Target_Pixel_Y)), (100, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (255, 255, 255), 2)

        if self.show_RCM_CB == True:
            cv2.circle(self.labelled_img, (self.RCM_PIXEL_X, self.RCM_PIXEL_Y), radius =5, color = (255,0,0),thickness = -1)

        if self.show_stacked_images_CB == True:
            if self.frame_two_freezed == True:
                if self.frame_two_freezed_captured == False:
                    self.freezed_image_two = copy.deepcopy(self.labelled_img)
                    self.frame_two_freezed_captured = True

            else:
                self.freezed_image_two = self.labelled_img
                self.frame_two_freezed_captured = False

            if self.frame_four_freezed == True:
                if self.frame_four_freezed_captured == False:
                    self.freezed_image_four = copy.deepcopy(self.labelled_img)
                    self.frame_four_freezed_captured = True

            else:
                self.freezed_image_four = self.labelled_img
                self.frame_four_freezed_captured = False

            self.labelled_img = self.show_live_image_stacked(self.img, self.freezed_image_two, self.labelled_img,
                                                             self.freezed_image_four)

        else:
            self.labelled_img = self.labelled_img

        # opens a new image detection cv window.... perform image detection stuff here
        if self.show_image_detection_window == True:
            self.image_detection_window()

    def image_freeze_frame(self, frame_number):
        if frame_number == 2:
            self.frame_two_freezed = not self.frame_two_freezed
        elif frame_number == 4:
            self.frame_four_freezed = not self.frame_four_freezed

    def select_origin(self):
        """select_origin calls when button is pressed.
        Opens up a window(Select Origin Window) copy of the current live single
        image frame for user to mark the origin point on the picture.

        Upon closing and reopening window, the previously marked points should
        still be marked"""

        if not self.origin_selected:
            self.select_origin_img = self.img

        else:
            self.select_origin_img = self.cache1img
        cv2.imshow("Select Origin Window", self.select_origin_img)
        cv2.setMouseCallback("Select Origin Window", self.Mouse_Callback_Origin)

    def Mouse_Callback_Origin(self, event, x, y, flags, param):
        """Mouse callback event using CV2

        Parameters
        ----------
        EVENT_LBUTTONDOWN: marks a point on the image, updates the Origin_Pixel_X, Origin_Pixel_Y values
        with the image pixel value when clicked
        EVENT_MBUTTONDOWN: clear markings on the image, returns a copy of the live image"
        EVENT_RBUTTONDOWN: display the pixel coordinate values(X,Y)of the marked points
        """
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.cache1img = copy.deepcopy(self.img)

            self.Origin_Pixel_X, self.Origin_Pixel_Y = x, y
            cv2.circle(self.cache1img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
            cv2.line(self.cache1img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), (self.Origin_Pixel_X, 2000),
                     (255, 255, 255), 3)
            cv2.imshow("Select Origin Window", self.cache1img)
            self.origin_selected = True

        elif (event == cv2.EVENT_MBUTTONDOWN):
            self.cache1img = copy.deepcopy(self.img)

            self.Origin_Pixel_X, self.Origin_Pixel_Y = 0, 0
            self.origin_selected = False
            cv2.imshow("Select Origin Window", self.cache1img)

        elif (event == cv2.EVENT_RBUTTONDBLCLK):
            self.cache1img = copy.deepcopy(self.img)
            self.Origin_Pixel_X, self.Origin_Pixel_Y = 741, int(self.depth_lookup_dictionary.get(self.depth))
            cv2.circle(self.cache1img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
            cv2.line(self.cache1img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), (self.Origin_Pixel_X, 2000),
                     (255, 255, 255), 3)
            cv2.imshow("Select Origin Window", self.cache1img)
            self.origin_selected = True



        elif (event == cv2.EVENT_RBUTTONDOWN):
            cv2.putText(self.cache1img, '{}'.format((self.Origin_Pixel_X, self.Origin_Pixel_Y)), (100, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (255, 255, 255), 2)
            cv2.imshow("Select Origin Window", self.cache1img)
            self.origin_selected = True

    def select_target(self):
        """select_target calls when button is pressed. Opens up a window(Select Origin Window) copy of the current live single
           image frame for user to mark the origin point on the picture.

            Upon closing and reopening window, the previously marked points should
           still be marked"""

        if not self.target_selected:
            self.select_target_img = self.img

        else:
            self.select_target_img = self.cache3img
        cv2.imshow("Select Target Window", self.select_target_img)
        cv2.setMouseCallback("Select Target Window", self.Mouse_Callback_Target)

    def Mouse_Callback_Target(self, event, x, y, flags, param):
        """Mouse callback event using CV2

        Parameters
        ----------
        EVENT_LBUTTONDOWN: marks a point on the image, updates the Target_Pixel_X, Target_Pixel_Y values
        with the image pixel value when clicked
        EVENT_MBUTTONDOWN: clear markings on the image, returns a copy of the live image"
        EVENT_RBUTTONDOWN: display the pixel coordinate values(X,Y)of the marked points
        """
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.cache3img = copy.deepcopy(self.img)

            self.Target_Pixel_X, self.Target_Pixel_Y = x, y
            cv2.circle(self.cache3img, (self.Target_Pixel_X, self.Target_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)

            cv2.imshow("Select Target Window", self.cache3img)
            self.target_selected = True

        elif (event == cv2.EVENT_MBUTTONDOWN):
            self.cache3img = copy.deepcopy(self.img)

            self.Target_Pixel_X, self.Target_Pixel_Y = 0, 0
            self.target_selected = False
            cv2.imshow("Select Target Window", self.cache3img)

        elif (event == cv2.EVENT_RBUTTONDOWN):
            cv2.putText(self.cache3img, '{}'.format((self.Target_Pixel_X, self.Target_Pixel_Y)), (100, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (255, 255, 255), 2)
            cv2.imshow("Select Target Window", self.cache3img)
            self.target_selected = True

    def draw_needle_line(self):
        """draw_needle_line calls when draw needle button is clicked
        Opens up a window (Draw Needle Line Window) copy of the current live single
        image frame for user to draw the needle line

        Upon closing and reopening window, previous drawn line should still be marked """
        if self.draw_needle_line_selected == False:
            self.draw_needle_line_img = self.img

        else:
            self.draw_needle_line_img = self.cache2img
        cv2.imshow("Draw Needle Line Window", self.draw_needle_line_img)
        cv2.setMouseCallback("Draw Needle Line Window", self.Mouse_Callback_Needle_Line)

    def calculate_target_angle(self):
        try:
            y_difference = -(self.Needle_End_Pixel_Y - self.Needle_Start_Pixel_Y)
            x_difference = self.Needle_End_Pixel_X - self.Needle_Start_Pixel_X
            self.Alpha = math.atan(x_difference / y_difference)
            self.Alpha = self.Alpha / math.pi * 180
        except:
            print("ZERO DIVISION ERROR")
            pass

    def Mouse_Callback_Needle_Line(self, event, x, y, flags, param):
        """Mouse callback event using CV2

            Parameters
            ----------
            EVENT_LBUTTONDOWN: marks a point on the image, updates the Needle_Start_Pixel_X, Needle_Start_Pixel_Y values
            with the image pixel value when clicked
            EVENT_MBUTTONDOWN: clear markings on the image, returns a copy of the live image"
            EVENT_RBUTTONDOWN: marks the endpoint of the line, updates the Needle_End_Pixel_X, Needle_End_Pixel_Y values

            TODO: Currently user need to take into consideration of direction (Start to End point). If user clicked end to
            start point, direction will be wrong
            """
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.cache2img = copy.deepcopy(self.img)

            self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = x, y
            cv2.circle(self.cache2img, (self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y), radius=5,
                       color=(255, 0, 0),
                       thickness=-1)
            cv2.imshow("Draw Needle Line Window", self.cache2img)
            self.draw_needle_line_selected = True

        elif (event == cv2.EVENT_MBUTTONDOWN):
            self.cache2img = copy.deepcopy(self.img)
            self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = 0, 0
            self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = 0, 0
            self.draw_needle_line_selected = False
            cv2.imshow("Draw Needle Line Window", self.cache2img)

        elif (event == cv2.EVENT_RBUTTONDOWN):
            self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = x, y
            cv2.circle(self.cache2img, (self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y), radius=5, color=(0, 0, 255),
                       thickness=-1)
            cv2.line(self.cache2img, (self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y),
                     (self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y),
                     (255, 255, 255), 3)

            """calculate and updates the target angle, x_distance, d_distance"""
            self.calculate_target_angle()
            self.calculate_change_x()

            self.draw_needle_line_selected = True
            cv2.imshow("Draw Needle Line Window", self.cache2img)

        elif (event == cv2.EVENT_RBUTTONDBLCLK):
            hypo_length = int(math.sqrt((self.Needle_End_Pixel_X-self.Needle_Start_Pixel_X)**2+(self.Needle_End_Pixel_Y-self.Needle_Start_Pixel_Y)**2))
            rotation_rectangle = (((self.Needle_End_Pixel_X+self.Needle_Start_Pixel_X)/2,(self.Needle_End_Pixel_Y+self.Needle_Start_Pixel_Y)/2),(int(9/self.mm_per_pixel),hypo_length),self.Alpha)
            self.box = cv2.boxPoints(rotation_rectangle)
            self.box = np.int0(self.box)
            rectangle = cv2.drawContours(self.cache2img,[self.box],0,(0,0,255),2)
            cv2.imshow("Draw Needle Line Window", self.cache2img)

    def Convert_Pixel_to_US_Coord(self):
        """Converts the pixel coordinates to the US coordinates in terms of mm.
        Requires the self.mm_per_pixel to convert.
        Gets the Coordinates of the surface (intersection of the extrapolated needle line and the horizontal line passing through origin)
        updates the values of the US Coordinates
        """
        try:
            # Currently not used
            # self.X_US_coordinates = (self.Target_Pixel_X - self.Origin_Pixel_X) * self.mm_per_pixel
            # self.Y_US_coordinates = (self.Target_Pixel_Y - self.Origin_Pixel_Y) * self.mm_per_pixel

            # self.distance_target_pixel = math.sqrt(
            #     (self.Target_Pixel_X - self.Origin_Pixel_X) ** 2 + (self.Target_Pixel_Y - self.Origin_Pixel_Y) ** 2)
            # self.distance_target_US = self.distance_target_pixel * self.mm_per_pixel
            self.calculate_change_d()

            self.gradient = (self.Needle_End_Pixel_Y - self.Needle_Start_Pixel_Y) / (
                    self.Needle_End_Pixel_X - self.Needle_Start_Pixel_X)
            self.intersect = self.Needle_End_Pixel_Y - (
                    self.gradient * self.Needle_End_Pixel_X)  # using y=mx+c, to get c

            self.Surface_Pixel_X = (self.Origin_Pixel_Y - self.intersect) / self.gradient
            self.Surface_Pixel_Y = self.Origin_Pixel_Y

            self.Surface_US_X = (self.Surface_Pixel_X - self.Origin_Pixel_X) * self.mm_per_pixel
            self.Surface_US_Y = (self.Surface_Pixel_Y - self.Origin_Pixel_Y) * self.mm_per_pixel

            self.calculate_UR_robot_move()

            self.calculate_projected_needle_pixel()  # Needle position after end up moving
            self.calculate_intended_needle_pixel()  # Needle position as of current


        except Exception as e:
            print(e)

    def set_values(self, attributes, value):
        attributes = value
        return

    def calculate_change_x(self):
        if self.Alpha == 0:
            pass
        else:
            self.Alpha_in_radians = self.Alpha / 180 * math.pi
            # x = (403.78 * math.sin(0.18444 * math.pi - self.Alpha_in_radians)) / (
            #     math.sin(0.41405 * math.pi + self.Alpha_in_radians))
            """Need to use the RCM_X and RCM_Y pt to calculate the hypo to fixed pt first"""
            self.RCM_US_distance_x_mm= (self.RCM_PIXEL_X-self.Origin_Pixel_X)*self.mm_per_pixel
            self.RCM_US_distance_y_mm = (self.RCM_PIXEL_Y-self.Origin_Pixel_Y)*self.mm_per_pixel
            a = (238.16- self.RCM_US_distance_x_mm)
            b = (294.80+ self.RCM_US_distance_y_mm)
            print("RCM distance to fixed pt x is: ")
            print(a)
            print("RCM distance to fixed pt y is: ")
            print(b)


            ratio_b_a = b/a
            hypo = math.sqrt(a**2+b**2)
            angle_between_alpha_arctan = ((math.pi/2)-(math.atan(ratio_b_a))- self.Alpha_in_radians)
            x = hypo/ math.sin(math.pi- angle_between_alpha_arctan - (math.atan(ratio_b_a)+(15.47/180*math.pi))) * math.sin(angle_between_alpha_arctan)
            self.actuator_move_value = 170 - x
            self.x_distance = x
            self.lookup_error_correction(self.actuator_move_value, 5)

    def calculate_change_d(self):
        error_correction_dict = {}
        self.Alpha_in_radians = self.Alpha / 180 * math.pi
        # d = 46.33 * math.sin(0.1200 * math.pi + self.Alpha_in_radians) / math.sin(
        #     (math.pi / 2) - self.Alpha_in_radians)
        hypo_1 = math.sqrt(self.RCM_US_distance_x_mm**2 + self.RCM_US_distance_y_mm**2)
        angle = math.atan(self.RCM_US_distance_x_mm/self.RCM_US_distance_y_mm) +self.Alpha_in_radians
        d = hypo_1 / math.sin((math.pi/2)-self.Alpha_in_radians)*math.sin(angle)

        # Error_correction_value = float(self.error_correction_value)
        Error_correction_value = 0
        self.d_distance = d + Error_correction_value

    def calculate_UR_robot_move(self):
        self.robot_move_value = self.d_distance - self.Surface_US_X

    def calculate_projected_needle_pixel(self):
        """Projected line is currently the line that shows after frame change
        TODO: swap this with intended line!"""
        self.Projected_Needle_Start_Pixel_X = self.Needle_Start_Pixel_X + int(self.robot_move_value / self.mm_per_pixel)
        self.Projected_Needle_End_Pixel_X = self.Needle_End_Pixel_X + int(self.robot_move_value / self.mm_per_pixel)

        self.Projected_Needle_Start_Pixel_Y = int(self.Needle_Start_Pixel_Y)
        self.Projected_Needle_End_Pixel_Y = int(self.Needle_End_Pixel_Y)

    def calculate_intended_needle_pixel(self):
        """Intended line is currently the line that shows the needle driver line before frame change... the trajectory line it will take when being inserted"""
        self.Intended_Needle_End_US_Y = 0
        self.Intended_Needle_End_US_X = self.d_distance

        self.Intended_Needle_End_Pixel_Y = int(self.Origin_Pixel_Y + self.Intended_Needle_End_US_Y / self.mm_per_pixel)
        self.Intended_Needle_End_Pixel_X = int(self.Origin_Pixel_X + self.Intended_Needle_End_US_X / self.mm_per_pixel)

        self.Intended_Needle_Start_Pixel_X = 0
        self.Intended_Needle_Start_Pixel_Y = int(
            self.Intended_Needle_End_Pixel_Y - self.Intended_Needle_End_Pixel_X * self.gradient)

    def lookup_error_correction(self, value, base=5):
        new_value = base * round(value / base)
        # dictionary_round_value = {"40": 10.86, "45": 11.01, "50": 11.16, "55": 11.86, "60": 12.25, "65": 11.74,
        #                           "70": 10.83, "75": 10.61,
        #                           "80": 10.39, "85": 11.47, "90": 13.34, "95": 13.85}
        dictionary_round_value = {"40": 0, "45": 0, "50": 0, "55": 0, "60": 0, "65": 0,
                                  "70": 0, "75": 0,
                                  "80": 0, "85": 0, "90": 0, "95": 0}
        self.error_correction_value = str(dictionary_round_value.get(str(new_value)))

    def image_detection_window(self):
        gray_image = self.img
        # gray_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.edited_frame = copy.deepcopy(self.img)

        gray_frame = cv2.GaussianBlur(gray_image, (21, 21), 0)
        if not self.initialise_canvas:
            self.blank_canvas = np.zeros_like(gray_frame)
            self.initialise_canvas = True

        if self.initialState is None:
            self.initialState = gray_frame
            return

        differ_frame = cv2.absdiff(self.initialState, gray_frame)

        # thresh_frame = differ_frame
        thresh_frame = cv2.threshold(differ_frame, 30, 255, cv2.THRESH_BINARY)[1]

        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # For the moving object in the frame finding the coutours

        # self.imgStack = self.stackImages(0.40,([self.img,self.img],[self.img,self.img]))

        cont, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #
        for cur in cont:
            #
            if cv2.contourArea(cur) < 50 or len(cont) > 3 or cv2.contourArea(cur) > 500:
                continue
            #
            (cur_x, cur_y, cur_w, cur_h) = cv2.boundingRect(cur)
            #
            M = cv2.moments(cur)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            #     print(cX, cY)
            if ((682<=cX<=1178) and (5<=cY<=463)):
                self.coord_list.append([cX, cY])

                self.image_detection_coord_list.append([cX, cY])
                cv2.drawContours(self.edited_frame, [cur], -1, (0, 255, 0), 2)
                cv2.circle(self.edited_frame, (cX, cY), 7, (255, 255, 255), -1)
                # To create a rectangle of green color around the moving object
                #
                cv2.rectangle(self.edited_frame, (cur_x, cur_y), (cur_x + cur_w, cur_y + cur_h), (0, 255, 0), 3)

                cv2.circle(self.blank_canvas, (cX, cY), 7, (255, 255, 0), -1)
            #     # from the frame adding the motion status
            #
        self.superimpose_img = cv2.bitwise_or(self.img, self.blank_canvas)

        # # stack image
        self.imgStack = self.stackImages(0.40,
                                         ([self.img, self.edited_frame], [self.blank_canvas, self.superimpose_img]))

        # self.superimpose_img = copy.deepcopy(self.img)
        if not self.kill_image_detection_window:
            cv2.imshow("stack_img", self.imgStack)
            # Creating a key to wait
            wait_key = cv2.waitKey(1)

        # With the help of the 'm' key ending the whole process of our system


        """Press 'm' key to clear all points"""
        if wait_key == ord('m'):
            self.image_detection_coord_list = []
            self.initialise_canvas = False

        """Press 's' key to draw best fit line"""
        if wait_key == ord('s'):
            if len(self.coord_list) > 3:
                self.curr_x, self.curr_y = 0, 0
                self.prev_x, self.prev_y = 0, 0
                self.tol_x = 20
                self.tol_y = 20
                self.initialise = False
                for idx, i in enumerate(self.coord_list):
                    # print(idx, i)
                    if self.curr_x == 0 and self.curr_y == 0:
                        self.initialise = True
                        self.prev_x, self.prev_y = i[0], i[1]

                    curr_x, curr_y = i[0], i[1]
                    if ((self.prev_x - self.curr_x) < -self.tol_x) or (
                            (self.curr_y - self.prev_y) < -self.tol_y) and self.initialise == True:
                        self.coord_list.pop(idx)
                    else:
                        self.prev_x, self.prev_y = i[0], i[1]
            coord_array = np.array(self.coord_list)

            # coord_array = np.array(self.coord_list)
            [vx, vy, x0, y0] = cv2.fitLine(coord_array, cv2.DIST_L1, 0, 0.01, 0.01)
            #
            # print(vx, vy, x0, y0)
            y_axis = np.array([0, 1])  # unit vector in the same direction as the x axis
            your_line = np.array(vx[0], vy[0])  # unit vector in the same direction as your line
            dot_product = np.dot(y_axis, your_line)
            angle_2_y = np.arcsin(dot_product)
            # print(angle_2_y)
            #
            angle_2_y_in_degree = (angle_2_y / math.pi * 180)
            best_fit_angle = "_" + str(angle_2_y_in_degree[1]) + "_"
            #     # Releasing the video
            #
            (x0, y0), (x1, y1) = self.calculateBestFitLine(vx[0], vy[0], x0[0], y0[0])
            cv2.line(self.edited_frame, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)
            cv2.line(self.blank_canvas, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)

            # cv2.line(self.superimpose_img, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)
            print(best_fit_angle)
            img = Image.fromarray(self.edited_frame)
            img.save(str(best_fit_angle)+"edited_img")

            img1 = Image.fromarray(self.blank_canvas)
            img1.save(str(best_fit_angle)+"blank_canvas")


        if wait_key == ord('q'):
            self.kill_image_detection_window = True
            cv2.destroyAllWindows()

        self.initialState = None

    def image_detection_window(self):
        gray_image = self.img
        # gray_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.edited_frame = copy.deepcopy(self.img)

        gray_frame = cv2.GaussianBlur(gray_image, (21, 21), 0)
        if not self.initialise_canvas:
            self.blank_canvas = np.zeros_like(gray_frame)
            self.initialise_canvas = True

        if self.initialState is None:
            self.initialState = gray_frame
            return

        differ_frame = cv2.absdiff(self.initialState, gray_frame)

        # thresh_frame = differ_frame
        thresh_frame = cv2.threshold(differ_frame, 30, 255, cv2.THRESH_BINARY)[1]

        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # For the moving object in the frame finding the coutours

        # self.imgStack = self.stackImages(0.40,([self.img,self.img],[self.img,self.img]))

        cont, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #
        for cur in cont:
            #
            if cv2.contourArea(cur) < 50 or len(cont) > 3 or cv2.contourArea(cur) > 500:
                continue
            #
            (cur_x, cur_y, cur_w, cur_h) = cv2.boundingRect(cur)
            #
            M = cv2.moments(cur)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            #     print(cX, cY)
            if ((682<=cX<=1178) and (5<=cY<=463)):
                self.coord_list.append([cX, cY])

                self.image_detection_coord_list.append([cX, cY])
                cv2.drawContours(self.edited_frame, [cur], -1, (0, 255, 0), 2)
                cv2.circle(self.edited_frame, (cX, cY), 7, (255, 255, 255), -1)
                # To create a rectangle of green color around the moving object
                #
                cv2.rectangle(self.edited_frame, (cur_x, cur_y), (cur_x + cur_w, cur_y + cur_h), (0, 255, 0), 3)

                cv2.circle(self.blank_canvas, (cX, cY), 7, (255, 255, 0), -1)
            #     # from the frame adding the motion status
            #
        self.superimpose_img = cv2.bitwise_or(self.img, self.blank_canvas)

        # # stack image
        self.imgStack = self.stackImages(0.40,
                                         ([self.img, self.edited_frame], [self.blank_canvas, self.superimpose_img]))

        # self.superimpose_img = copy.deepcopy(self.img)
        if not self.kill_image_detection_window:
            cv2.imshow("stack_img", self.imgStack)
            # Creating a key to wait
            wait_key = cv2.waitKey(1)

        # With the help of the 'm' key ending the whole process of our system


        """Press 'm' key to clear all points"""
        if wait_key == ord('m'):
            self.image_detection_coord_list = []
            self.initialise_canvas = False

        """Press 's' key to draw best fit line"""
        if wait_key == ord('s'):
            if len(self.coord_list) > 3:
                self.curr_x, self.curr_y = 0, 0
                self.prev_x, self.prev_y = 0, 0
                self.tol_x = 20
                self.tol_y = 20
                self.initialise = False
                for idx, i in enumerate(self.coord_list):
                    # print(idx, i)
                    if self.curr_x == 0 and self.curr_y == 0:
                        self.initialise = True
                        self.prev_x, self.prev_y = i[0], i[1]

                    curr_x, curr_y = i[0], i[1]
                    if ((self.prev_x - self.curr_x) < -self.tol_x) or (
                            (self.curr_y - self.prev_y) < -self.tol_y) and self.initialise == True:
                        self.coord_list.pop(idx)
                    else:
                        self.prev_x, self.prev_y = i[0], i[1]
            coord_array = np.array(self.coord_list)

            # coord_array = np.array(self.coord_list)
            [vx, vy, x0, y0] = cv2.fitLine(coord_array, cv2.DIST_L1, 0, 0.01, 0.01)
            #
            # print(vx, vy, x0, y0)
            y_axis = np.array([0, 1])  # unit vector in the same direction as the x axis
            your_line = np.array(vx[0], vy[0])  # unit vector in the same direction as your line
            dot_product = np.dot(y_axis, your_line)
            angle_2_y = np.arcsin(dot_product)
            # print(angle_2_y)
            #
            angle_2_y_in_degree = (angle_2_y / math.pi * 180)
            best_fit_angle = "_" + str(angle_2_y_in_degree[1]) + "_"
            #     # Releasing the video
            #
            (x0, y0), (x1, y1) = self.calculateBestFitLine(vx[0], vy[0], x0[0], y0[0])
            cv2.line(self.edited_frame, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)
            cv2.line(self.blank_canvas, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)

            # cv2.line(self.superimpose_img, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)
            print(best_fit_angle)
            img = Image.fromarray(self.edited_frame)
            img.save(str(best_fit_angle)+"edited_img")

            img1 = Image.fromarray(self.blank_canvas)
            img1.save(str(best_fit_angle)+"blank_canvas")


        if wait_key == ord('q'):
            self.kill_image_detection_window = True
            cv2.destroyAllWindows()

        self.initialState = None

    def Mouse_Callback_Draw_RCM01(self, event, x, y, flags, param):
        """Mouse callback event using CV2

        Parameters
        ----------
        EVENT_LBUTTONDOWN: marks a point on the image, updates the RCM01_START_PIXEL_X, RCM01_START_PIXEL_Y values
        with the image pixel value when clicked
        EVENT_MBUTTONDOWN: clear markings on the image, returns a copy of the live image"
        EVENT_RBUTTONDOWN: marks the end pt of the RCM01 line, updates the RCM01_END_PIXEL_X, RCM_END_PIXEL_Y values
        with the image pixel value when clicked
        """
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.cache4_img = copy.deepcopy(self.img)

            self.RCM_01_START_PIXEL_X, self.RCM_01_START_PIXEL_Y = x,y
            cv2.circle(self.cache4_img,(self.RCM_01_START_PIXEL_X, self.RCM_01_START_PIXEL_Y),radius = 5, color =(255,0,0), thickness=-1)
            cv2.imshow("DRAW_RCM_LINE_01",self.cache4_img)
            self.draw_RCM_01_bool = True

        elif (event == cv2.EVENT_MBUTTONDOWN):
            self.cache4_img = copy.deepcopy(self.img)
            self.RCM_01_START_PIXEL_X, self.RCM_01_START_PIXEL_Y = 0,0
            self.RCM_01_END_PIXEL_X, self.RCM_01_END_PIXEL_Y = 0,0
            self.draw_RCM_01_bool = False
            cv2.imshow("DRAW_RCM_LINE_01", self.cache4_img)

        elif (event == cv2.EVENT_RBUTTONDOWN):
            self.RCM_01_END_PIXEL_X, self.RCM_01_END_PIXEL_Y = x,y
            cv2.circle(self.cache4_img, (self.RCM_01_END_PIXEL_X,self.RCM_01_END_PIXEL_Y),radius = 5, color = (0,0,255), thickness = -1)
            cv2.line(self.cache4_img, (self.RCM_01_START_PIXEL_X, self.RCM_01_START_PIXEL_Y),(self.RCM_01_END_PIXEL_X, self.RCM_01_END_PIXEL_Y), (255, 255, 255), 3)

            self.calculate_equation_RCM_01()
            self.draw_RCM_01_bool = True
            cv2.imshow("DRAW_RCM_LINE_01", self.cache4_img)


    def Mouse_Callback_Draw_RCM02(self, event, x, y, flags, param):
        """Mouse callback event using CV2

        Parameters
        ----------
        EVENT_LBUTTONDOWN: marks a point on the image, updates the RCM01_START_PIXEL_X, RCM01_START_PIXEL_Y values
        with the image pixel value when clicked
        EVENT_MBUTTONDOWN: clear markings on the image, returns a copy of the live image"
        EVENT_RBUTTONDOWN: marks the end pt of the RCM01 line, updates the RCM01_END_PIXEL_X, RCM_END_PIXEL_Y values
        with the image pixel value when clicked
        """
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.cache5_img = copy.deepcopy(self.img)

            self.RCM_02_START_PIXEL_X, self.RCM_02_START_PIXEL_Y = x, y
            cv2.circle(self.cache5_img, (self.RCM_02_START_PIXEL_X, self.RCM_02_START_PIXEL_Y), radius=5,
                       color=(255, 0, 0), thickness=-1)
            cv2.imshow("DRAW_RCM_LINE_02", self.cache5_img)
            self.draw_RCM_02_bool = True

        elif (event == cv2.EVENT_MBUTTONDOWN):
            self.cache5_img = copy.deepcopy(self.img)
            self.RCM_02_START_PIXEL_X, self.RCM_02_START_PIXEL_Y = 0, 0
            self.RCM_02_END_PIXEL_X, self.RCM_02_END_PIXEL_Y = 0, 0
            self.draw_RCM_02_bool = False
            cv2.imshow("DRAW_RCM_LINE_02", self.cache5_img)

        elif (event == cv2.EVENT_RBUTTONDOWN):
            self.RCM_02_END_PIXEL_X, self.RCM_02_END_PIXEL_Y = x, y
            cv2.circle(self.cache5_img, (self.RCM_02_END_PIXEL_X, self.RCM_02_END_PIXEL_Y), radius=5, color=(0, 0, 255),
                       thickness=-1)
            cv2.line(self.cache5_img, (self.RCM_02_START_PIXEL_X, self.RCM_02_START_PIXEL_Y),
                     (self.RCM_02_END_PIXEL_X, self.RCM_02_END_PIXEL_Y), (255, 255, 255), 3)
            self.draw_RCM_02_bool = True
            self.calculate_equation_RCM_02()
            cv2.imshow("DRAW_RCM_LINE_02", self.cache5_img)



    def draw_RCM_Line(self,img_number):
        if img_number == 1:
            if not self.draw_RCM_01_bool:
                self.draw_RCM01_img = self.img

            else:
                self.draw_RCM01_img = self.cache4_img
            cv2.imshow("DRAW_RCM_LINE_01", self.draw_RCM01_img)
            cv2.setMouseCallback("DRAW_RCM_LINE_01", self.Mouse_Callback_Draw_RCM01)

        elif img_number == 2:
            if not self.draw_RCM_02_bool:
                self.draw_RCM02_img = self.img
            else:
                self.draw_RCM02_img = self.cache5_img
            cv2.imshow("DRAW_RCM_LINE_02", self.draw_RCM02_img)
            cv2.setMouseCallback("DRAW_RCM_LINE_02", self.Mouse_Callback_Draw_RCM02)


    def calculate_equation_RCM_01(self):
        self.gradient_RCM_01 = (self.RCM_01_END_PIXEL_Y-self.RCM_01_START_PIXEL_Y) / (self.RCM_01_END_PIXEL_X-self.RCM_01_START_PIXEL_X)
        self.intersect_RCM_01 = self.RCM_01_END_PIXEL_Y - (self.gradient_RCM_01 * self.RCM_01_END_PIXEL_X)
    def calculate_equation_RCM_02(self):
        self.gradient_RCM_02 = (self.RCM_02_END_PIXEL_Y - self.RCM_02_START_PIXEL_Y) / (
                    self.RCM_02_END_PIXEL_X - self.RCM_02_START_PIXEL_X)
        self.intersect_RCM_02 = self.RCM_02_END_PIXEL_Y - (self.gradient_RCM_02 * self.RCM_02_END_PIXEL_X)

    def calculate_RCM_px(self):
        self.RCM_PIXEL_X = int((self.intersect_RCM_02-self.intersect_RCM_01)/(self.gradient_RCM_01-self.gradient_RCM_02))
        self.RCM_PIXEL_Y = int(self.gradient_RCM_01*self.RCM_PIXEL_X + self.intersect_RCM_01)

    def overwrite_RCM_value(self):
        self.RCM_PIXEL_X = int((238.16-self.Overwrite_RCM_X_Entry_Value)/self.mm_per_pixel)+self.Origin_Pixel_X
        self.RCM_PIXEL_Y = int((self.Overwrite_RCM_Y_Entry_Value-294.80)/self.mm_per_pixel)+self.Origin_Pixel_Y

