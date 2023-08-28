import cv2
import US_Screen.constants as c
import pyigtl
class US_SCREEN:
    # def __init(self):
    #     self.cap = cv2.VideoCapture(0)
    #     self.width = c.WIDTH
    #     self.height = c.HEIGHT
    #     self.cap.set(3, self.width)
    #     self.cap.set(4, self.height)
    #
    # def show_orginal(self):
    #     success, img = self.cap.read()
    #     return img

    def __init__(self):

        self.client = pyigtl.OpenIGTLinkClient(host="192.168.0.200", port=18946)

    def show_original(self):
        message = self.client.wait_for_message(device_name="ImageToReference", timeout=3)
        img =message.image
        return img
