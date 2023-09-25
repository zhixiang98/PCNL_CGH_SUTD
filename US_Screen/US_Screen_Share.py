import cv2
import US_Screen.constants as c
import tkinter
import pyigtl
import time
import threading
import numpy as np

class US_SCREEN:
    # def __init__(self):
    #     self.cap = cv2.VideoCapture(0)
    #     self.width = c.WIDTH
    #     self.height = c.HEIGHT
    #     self.cap.set(3, self.width)
    #     self.cap.set(4, self.height)
    #
    # def show_original(self):
    #     # start_time = time.time()
    #     success, img = self.cap.read()
    #     # print(type(img))
    #     # print("FPS: ", 1.0 / (time.time() - start_time))
    #     return img


    def __init__(self):
        self.client = pyigtl.OpenIGTLinkClient(host="192.168.0.12", port=23338)
        # if self.client.is_connected()  == False:
        #     print("not connected")
        #     return
        self.message = None
        # self.imageSizeX = 1432
        # self.imageSizeY = 740
        self.imageSizeX = 716
        self.imageSizeY = 370


    def show_original(self):
        start_time = time.time()
        self.message = self.client.wait_for_message(device_name="USImage", timeout=5)
        img = self.message.image  # except:

        img = np.squeeze(img.reshape(1, self.imageSizeX, self.imageSizeY).transpose(0, 1, 2))
        # print(img)        # try:
        #     img = self.message.image        # except:
        # except:
        #     img = None

        return img


