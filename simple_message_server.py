import pyigtl  # pylint: disable=import-error
from math import cos, sin, pi
from time import sleep, time
import numpy as np


server = pyigtl.OpenIGTLinkServer(port=18944, local_server=True)

image_size = [400, 200]

timestep = 0

while True:

    start_time = time()

    if not server.is_connected():
        # Wait for client to connect
        sleep(0.1)
        continue

    timestep += 1
    # Generate image
    voxels = np.random.randn(1, image_size[1], image_size[0]) * 50 + 100
    image_message = pyigtl.ImageMessage(voxels, device_name="USImage")

    # Generate transform
    # matrix = np.eye(4)
    # matrix[0, 3] = sin(timestep * 0.01) * 20.0
    # rotation_angle_rad = timestep * 0.5 * pi / 180.0
    # matrix[1, 1] = cos(rotation_angle_rad)
    # matrix[2, 1] = -sin(rotation_angle_rad)
    # matrix[1, 2] = sin(rotation_angle_rad)
    # matrix[2, 2] = cos(rotation_angle_rad)
    # transform_message = pyigtl.TransformMessage(matrix, device_name="ImageToReference", timestamp=image_message.timestamp)
    #
    # # Generate string
    # string_message = pyigtl.StringMessage("TestingString_"+str(timestep), device_name="Text", timestamp=image_message.timestamp)

    # Send messages
    server.send_message(image_message)
    # server.send_message(transform_message)
    # server.send_message(string_message)

    # Print received messages
    messages = server.get_latest_messages()
    print("FPS: ", 1.0 / (time() - start_time))
    # print(string_message)
    print(time()-start_time)
    for message in messages:
        print(message.device_name)

    # Do not flood the message queue,
    # but allow a little time for background network transfer
    sleep(0.01)