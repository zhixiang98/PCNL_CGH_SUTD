import pyigtl  # pylint: disable=import-error
import cv2
from time import sleep
import numpy as np
from math import sin
import time
from PIL import Image

# server = pyigtl.OpenIGTLinkServer(port=18944)
server = pyigtl.OpenIGTLinkServer(port=18944, local_server=True)

# image = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# image.set(3,100)
# image.set(4,50)

# image = Image.open("sample_image01.png").convert("RGB")
# print(image.format)
# print(image.mode)
# print(image.size)
# print(image)
# numpydata = np.array(image)
# print(numpydata.shape)
# print(numpydata)

timestep = 0
while True:
    start_time = time.time()
    if not server.is_connected():
        # Wait for client to connect
        sleep(0.1)
        continue
    image = Image.open("GUI/sample_image01.png").convert("RGB")
    # Generate image

    voxels = np.asarray(image)
    voxels = voxels.transpose(0, 1, 2)
    voxels = np.squeeze(voxels)
    voxels=np.squeeze(voxels)

    print(voxels.shape)

    # ret,voxels = image.read()
    # voxels = np.asarray(voxels)
    # print(voxels.shape)

    # Send image
    # print(f"time: {timestep}")
    image_message = pyigtl.ImageMessage(voxels, device_name="USImage")
    server.send_message(image_message, wait=True)
    print(time.time()-start_time)
    print("FPS: ", 1.0 / (time.time() - start_time))

    # Since we wait until the message is actually sent, the message queue will not be flooded