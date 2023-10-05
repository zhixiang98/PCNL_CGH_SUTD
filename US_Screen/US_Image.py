import pyigtl
import time
import numpy as np
from PIL import Image
import cv2
import copy

class US_IMAGE():
    def __init__(self):
        #---Pixel Coordinates---
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
        self.Origin_Pixel_X , self.Origin_Pixel_Y = 0,0
        self.Target_Pixel_X, self.Target_Pixel_Y = 0,0
        self.Surface_Pixel_X, self.Surface_Pixel_Y =0,0

        self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = 0,0
        self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = 0, 0

        self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y = 0, 0
        self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y = 0, 0

        #---Ultrasound Coordinates---
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

        self.X_US_coordinates, self.Y_US_coordinates = 0,0 #currently not in used. to be used for target/ mouse selection to show distance between point and origin
        #--- Important values---
        """
        Theta is the angle measured from the drawn needle line with the vertical axis
        Alpha is the angle actual angle made from the inserted needle with the vertical axis
        x_distance is the fixed distance measured from the fixed point of the actuator to the needle
        d_distance is the horizontal distance measured from the probe to the needle 
        """

        self.Theta = 0
        self.Alpha = 0
        self.x_distance = 0 #x_distance is from the fixed point of actuator to needle
        self.d_distance = 0 #d_distance is the horizontal distance from the probe to the needle

        self.gradient = 0
        self.intersect = 0

        self.mm_per_pixel = 0 #mm per pixel provided by the US

        #---- igtl configuration ---------
        """
        host depends on the IP address of the US machine. Ideally try to make this same as robot/ FT-Sensor
        port also depends on the dedicated port of the US machine
        """
        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)
        self.client = pyigtl.OpenIGTLinkClient(host="192.168.0.106", port=23338)

        #----- image resolution received from the message. Resolution of the US machine (1432 x 740)
        self.imageSizeX = 1432
        self.imageSizeY = 740


        #--- Images for display ----
        """
        images in the formate of np nd_array to be used and passed on to the Overview
        all the image data should be named in the format of img
        
        self.img: main live time image that is displayed on the UI
        self.select_origin: image data of the drawn origin point of the US image
        self.cache1img: image data of the cache image of the drawn select_origin image
        self.cache2img: image data of the cache image of the drawn needle_line image
        
        """
        self.img = None #live time image that is shown on the UI, can be stacked or single parse to Overviews
        self.select_origin_img = None #select origin image
        self.cache1img = None # image that is "cleared" to be used for the select_origin function
        self.cache2img = None # image that is "cleared" to be used for the draw_needle_line function
        self.labelled_img = None #img that is finally displayed and pass to update canvas

        self.single_img = None
        self.stacked_img = None

        #----Boolean variables for origin button clicked------
        """
        Boolean variables that help to navigate the logic of the select_origin() and draw_needle_line()
        
        self.stacked_images_selected: False -> only the single live US will be shown, True -> stacked image of 2x2 will be shown
        """

        self.origin_selected = False
        self.draw_needle_line_selected = False

        self.stacked_images_selected = False


        #-----CheckBoxes-----------
        self.show_origin_CB = False
        self.show_needle_line_CB = False
        self.show_projected_needle_line_CB = False
        self.show_US_coordinate_CB = False
        self.show_target_CB = False



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


    def connect_igtl_client(self):
        """Reconnects to IGT client. Print "RECONNECTED_CLIENT upon success

        Parameters
        -----
        none currently #TODO create a text field for different host and port number

        Raises
        -------

        """
        self.client.stop() #stop connection first
        print("RECONNECTED_CLIENT")
        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)

    def receive_image_message(self):
        """Receives message from server. Currently only receiving IMAGE messages

        Parameters
        ----------
        none currently """

        # self.message = self.client.wait_for_message(device_name="USImage", timeout =5.0)

        # #used for igtl settings with US from CreativeMed
        # self.img = self.message.image
        # print(type(self.img))
        # self.single_img = np.squeeze(self.img.reshape(1,self.imageSizeY, self.imageSizeX).transpose(0,1,2))
        # self.single_img = np.asarray(self.single_img)

        self.img = Image.open("GUI/sample_image01.png").convert("RGB")
        self.img = np.asarray(self.img)



    def show_live_image(self,img1=None , img2=None, img3 =None, img4 =None):
        """
        Parse self.receive_image_message() that updates self.img
        Display a single live image of the Ultra Sound screen.
        Display different images based on the different CB
        """

        # #used for igtl settings with US from CreativeMed
        # self.receive_image_message()
        # if not self.stacked_images_selected:
        #     self.img = self.single_img
        # else:
        #     self.show_live_image_stacked(img1, img2, img3, img4)
        #     self.img = self.stacked_img
        #
        self.receive_image_message()

        # placeholder image

        self.labelled_img = copy.deepcopy(self.img)

        if self.show_origin_CB == True:
            cv2.circle(self.labelled_img, (self.Origin_Pixel_X, self.Origin_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
            cv2.line(self.labelled_img, (0, self.Origin_Pixel_Y), (2000, self.Origin_Pixel_Y), (255, 255, 255), 3)

        if self.show_needle_line_CB == True:
            cv2.line(self.labelled_img, (self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y),
                     (self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y), (255, 255, 255), 3)

        if self.show_projected_needle_line_CB:
            cv2.line(self.labelled_img, (self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y),
                     (self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y), (0, 255, 255), 3)

        if self.show_target_CB == True:
            cv2.circle(self.labelled_img, (self.Target_Pixel_X, self.Target_Pixel_Y), radius=5, color=(255, 0, 0),
                       thickness=-1)
        if self.show_US_coordinate_CB == True:
            cv2.putText(self.labelled_img, '{}'.format((self.Origin_US_X, self.Origin_US_Y)), (100, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (255, 255, 255), 2)




        # self.show_live_image_stacked(self.img,self.img,self.img,self.img)

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

    def Mouse_Callback_Origin(self, event, x, y,flags, param):
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

        elif (event == cv2.EVENT_RBUTTONDOWN):
            cv2.putText(self.cache1img, '{}'.format((self.Origin_Pixel_X, self.Origin_Pixel_Y)), (100, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (255, 255, 255), 2)
            cv2.imshow("Select Origin Window", self.cache1img)
            self.origin_selected = True


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
            cv2.circle(self.cache2img, (self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y), radius=5, color=(255, 0, 0),
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
            self.draw_needle_line_selected = True
            cv2.imshow("Draw Needle Line Window", self.cache2img)


    def Convert_Pixel_to_US_Coord(self):
        """Converts the pixel coordinates to the US coordinates in terms of mm.
        Requires the self.mm_per_pixel to convert.
        Gets the Coordinates of the surface (intersection of the extrapolated needle line and the horizontal line passing through origin)
        updates the values of the US Coordinates
        """
        self.X_US_coordinates = (self.Target_Pixel_X - self.Origin_Pixel_X) * self.mm_per_pixel
        self.Y_US_coordinates = (self.Target_Pixel_Y - self.Origin_Pixel_Y) * self.mm_per_pixel

        self.gradient = (self.Needle_End_Pixel_Y-self.Needle_Start_Pixel_Y) / (self.Needle_End_Pixel_X-self.Needle_Start_Pixel_X)
        self.intersect = self.Needle_End_Pixel_Y - (self.gradient*self.Needle_End_Pixel_X) #using y=mx+c, to get c

        self.Surface_Pixel_X = (self.Origin_Pixel_Y-self.intersect) / self.gradient
        self.Surface_Pixel_Y = self.Origin_Pixel_Y

        self.Surface_US_X = (self.Surface_Pixel_X - self.Origin_Pixel_X) * self.mm_per_pixel
        self.Surface_US_Y = (self.Surface_Pixel_Y - self.Origin_Pixel_Y) * self.mm_per_pixel

    def Calculation_x_distance(self):


    def set_values(self, attributes, value):
        attributes = value
        return


# a = US_IMAGE()
# while True:
#     b = (a.show_original_image())