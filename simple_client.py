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


directory = r"C:\Users\Zhi Xiang\Desktop\pythonProject\PCNL_CGH_SUTD\Img_source_four"

# cv2.namedWindow("test")
# client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)

# client = pyigtl.OpenIGTLinkClient(host="192.168.1.9", port=18944)
client = pyigtl.OpenIGTLinkClient(host="192.168.1.47", port=23338)

os.chdir(directory)


# client = pyigtl.OpenIGTLinkClient(host="192.168.0.106", port=23338)
# client = pyigtl.OpenIGTLinkClient(host="127.0.0.1", port=18944)


imageSizeX, imageSizeY = 740 , 1432

while True:
    curr_datetime = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    file_name = curr_datetime +".png"
    # start_time = time.time()
    response = input("letter")
    if response == "a":
        message = client.wait_for_message("USImage", timeout=10)

    # try:
    #     # print(message.image)
    # except:
    #     pass
    # print(time.time()-start_time)
    try:

        print(message)
        img = message.image
        print(message.image.shape)




        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.squeeze(message.image.reshape(1, imageSizeX, imageSizeY).transpose(0, 1, 2))
        img = Image.fromarray(img)
        img.save(file_name)
        # time.sleep(10)
    except Exception as error:
        print(error)


    # time.sleep(2)


    # try:
    #     img = message.image
    #     print(message.image.shape)
    #
    # # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     img = np.squeeze(img.reshape(1, imageSizeX, imageSizeY).transpose(0,1,2))
    #     img = Image.fromarray(img)
    #     img.save(file_name)
    # except:
    #     print("image not saved!")
    # try:
    #     print("FPS: ", 1.0 / (time.time() - start_time))
    #     # print(img.shape)
    # except:
    #     pass
    # # try:
    # #     img = message.image
    # #     img = Image.fromarray(img, 'RGB')
    # #     img.save(curr_datetime)
    # # except:
    # #     print("img not saved!")
    #
    # # print("FPS: ", 1.0 / (time.time() - start_time))
    #
    # # cv2.imshow("test", img)
    # #
    # # # # print(message.image)
    # # if cv2.waitKey(1) == ord('q'):
    # #     cv2.destroyAllWindows()
    # #     break