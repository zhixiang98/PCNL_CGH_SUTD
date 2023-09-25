"""
============================
Simple client
============================

Simplest example of getting an image from a device and saving

"""
import time
import pyigtl  # pylint: disable=import-error
import cv2
from PIL import Image
import os
from datetime import datetime
import numpy as np


directory = r"C:\Users\zhixi\Documents\PCNL_CGH_SUTD\Img_source"

# cv2.namedWindow("test")
# client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)

client = pyigtl.OpenIGTLinkClient(host="192.168.0.12", port=23338)

os.chdir(directory)

imageSizeX, imageSizeY = 740 , 1432

while True:
    curr_datetime = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    file_name = curr_datetime +".png"
    start_time = time.time()
    message = client.wait_for_message("USImage", timeout=5.0)

    # try:
    #     # print(message.image)
    # except:
    #     pass
    print(time.time()-start_time)
    img = message.image
    print(message.image.shape)

    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img = np.squeeze(message.image.reshape(1, imageSizeX, imageSizeY).transpose(0, 1, 2))
    # img = Image.fromarray(img)
    # img.save(file_name)


    try:
        img = message.image
        print(message.image.shape)

    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.squeeze(img.reshape(1, imageSizeX, imageSizeY).transpose(0,1,2))
        img = Image.fromarray(img)
        img.save(file_name)
    except:
        print("image not saved!")
    try:
        print("FPS: ", 1.0 / (time.time() - start_time))
        # print(img.shape)
    except:
        pass
    # try:
    #     img = message.image
    #     img = Image.fromarray(img, 'RGB')
    #     img.save(curr_datetime)
    # except:
    #     print("img not saved!")

    # print("FPS: ", 1.0 / (time.time() - start_time))

    # cv2.imshow("test", img)
    #
    # # # print(message.image)
    # if cv2.waitKey(1) == ord('q'):
    #     cv2.destroyAllWindows()
    #     break