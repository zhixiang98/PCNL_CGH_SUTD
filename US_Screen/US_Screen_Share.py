import cv2
import constants as c
from helpers import *


class US_Screen():
    def __init(self):
        self.cap = cv2.VideoCapture(0)
        self.width = c.WIDTH
        self.height = c.HEIGHT
        self.cap.set(3,self.width)
        self.cap.set(4,self.height)

    def show_orginal(self):
        success,img = self.cap.read()
        return img