import pyigtl
import time
import numpy as np
from PIL import Image


class US_IMAGE():
    def __init__(self):
        #---Pixel Coordinates---
        self.Origin_Pixel_X , self.Origin_Pixel_Y = 0,0
        self.Target_Pixel_X, self.Target_Pixel_Y = 0,0
        self.Surface_Pixel_X, self.Surface_Pixel_Y =0,0

        self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = 0,0
        self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = 0, 0

        self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y = 0, 0
        self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y = 0, 0

        #---Ultrasound Coordinates---
        self.Origin_US_X, self.Origin_US_Y = 0, 0
        self.Needle_Start_US_X, self.Needle_Start_US_Y = 0, 0
        self.Needle_End_US_X, self.Needle_End_US_Y = 0, 0
        self.Surface_US_X, self.Surface_US_Y = 0, 0

        #--- Important values---
        self.Theta = 0
        self.Alpha = 0
        self.x_distance = 0 #x_distance is from the fixed point of actuator to needle
        self.d_distance = 0 #d_distance is the horizontal distance from the probe to the needle

        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)
        self.client = pyigtl.OpenIGTLinkClient(host="192.168.0.106", port=23338)

        self.imageSizeX = 1432
        self.imageSizeY = 740

        print(self.client.is_connected())

        self.img = None


    def connect_igtl_client(self):
        self.client.stop()
        print("RECONNECTED_CLIENT")
        # self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)

    def receive_image_message(self):
        self.message = self.client.wait_for_message(device_name="USImage", timeout =5.0)

        # print(self.message)

        self.img = self.message.image
        print(type(self.img))
        self.img = np.squeeze(self.img.reshape(1,self.imageSizeY, self.imageSizeX).transpose(0,1,2))
        self.img = np.asarray(self.img)




    #
    #     except Exception as error:
    #         print("Error image message not received!")
    #         print(error)

    def show_original_image(self):
        self.receive_image_message()


    def set_values(self, attributes, value):
        attributes = value
        return


# a = US_IMAGE()
# while True:
#     b = (a.show_original_image())