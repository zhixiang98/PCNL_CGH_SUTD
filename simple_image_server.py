import pyigtl  # pylint: disable=import-error
import cv2
from time import sleep
import numpy as np
from math import sin
import time
# server = pyigtl.OpenIGTLinkServer(port=18944)
server = pyigtl.OpenIGTLinkServer(port=18944, local_server=False)
# server = pyigtl.OpenIGTLinkServer(port=18944, local_server=False)


image = cv2.VideoCapture(0)
image.set(3,1080)
image.set(4,720)

timestep = 0
while True:
    start_time = time.time()
    if not server.is_connected():
        # Wait for client to connect
        # print("Server not connected!")
        sleep(0.1)
        continue

    # Generate image


    ret,voxels = image.read()
    # voxels = np.asarray(voxels)
    # print(voxels.shape)

    # Send image
    # print(f"time: {timestep}")
    image_message = pyigtl.ImageMessage(voxels, device_name="USImage")
    server.send_message(image_message, wait=True)
    print(time.time()-start_time)
    print("FPS: ", 1.0 / (time.time() - start_time))

    # Since we wait until the message is actually sent, the message queue will not be flooded
    # sleep(0.1)
