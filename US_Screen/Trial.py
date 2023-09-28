import pyigtl
import time
import numpy as np
from PIL import Image
import US_Image
import tkinter



class TRIAL():
    def __init__(self):
        self.client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)
        self.message = None
        self.repeat()

    def connect_igtl_client(self):
        self.client.stop()
        self.client = pyigtl.OpenIGTLinkClient(host = "127.0.0.1", port = 18944)

    def receive_image_message(self):
        self.message = self.client.wait_for_message(device_name="USImage", timeout=5)

        print(self.message)
        try:
            img = self.message.image
            return img
        except:
            pass
            print("NO IMAGE RECEIVED")
        print("END OF RECEIVE IMAGE FUNCTION")

        # img = np.squeeze(img.reshape(1, self.imageSizeX, self.imageSizeY).transpose(0, 1, 2))

    #
    #     except Exception as error:
    #         print("Error image message not received!")
    #         print(error)

    def show_original_image(self):
        self.img = self.receive_image_message()
        # used for displaying static image currently as placeholder...
        # img = Image.open("../GUI/sample_image01.png").convert("RGB")
        print(self.img)
        self.img = np.asarray(self.img)
        #
        #
        return self.img

    def set_values(self, attributes, value):
        attributes = value
        return

    def repeat(self):
        image = self.receive_image_message()
        print(image)
        self.repeat()


A = TRIAL()
A.connect_igtl_client()
B = A.show_original_image()
print(B)