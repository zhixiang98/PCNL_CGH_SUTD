"""
============================
Simple client
============================

Simplest example of getting a image and displaying on CV window

"""
import time
import pyigtl  # pylint: disable=import-error
import cv2

client = pyigtl.OpenIGTLinkClient(host="192.168.0.12", port=23338)

# client = pyigtl.OpenIGTLinkClient(host="192.168.0.106", port=23338)
while True:
    start_time = time.time()
    message = client.wait_for_message("USImage", timeout=5.0)

    try:
        # print(message)
        print(message.image.shape)
    except:
        print("no_image_message_received")
    print(time.time()-start_time)
    try:
        img = message.image
    except:
        print("CV2_no_image")

    try:
        print("FPS: ", 1.0 / (time.time() - start_time))
    except:
        pass
    cv2.imshow("test", img)

    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break