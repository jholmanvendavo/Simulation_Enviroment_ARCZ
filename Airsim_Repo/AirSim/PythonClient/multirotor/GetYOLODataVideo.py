import threading
import time
import airsim
import pprint
import cv2
import numpy as np
from PythonClient.multirotor.processor import MediaProcessor

import supervision as sv
from ultralytics import YOLO



import os
# connect to the AirSim simulator
client = airsim.MultirotorClient()
client2 = airsim.VehicleClient()
client2.confirmConnection()
client.confirmConnection()
client.enableApiControl(True)
#
state = client.getMultirotorState()
s = pprint.pformat(state)
print("state: %s" % s)
#
imu_data = client.getImuData()
s = pprint.pformat(imu_data)
print("imu_data: %s" % s)

barometer_data = client.getBarometerData()
s = pprint.pformat(barometer_data)
print("barometer_data: %s" % s)
#
magnetometer_data = client.getMagnetometerData()
s = pprint.pformat(magnetometer_data)
print("magnetometer_data: %s" % s)
#
gps_data = client.getGpsData()
s = pprint.pformat(gps_data)
print("gps_data: %s" % s)


global stop_thread1
# Set up video writer
global out
camera_name = "1"  # Change this to the name of your camera (e.g., 'front', 'bottom', etc.)
image_type = airsim.ImageType.Scene
video_output = 'c:/Users/jholman/Documents/AirSim/Test/video2.avi'  # Change this to your desired output path
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Use 'MJPG' codec
frame_width, frame_height = 1280, 1080 #Update with your desired frame size
out = cv2.VideoWriter(video_output, fourcc, 20.0, (frame_width, frame_height))
#


# Define the first function to run in a separate thread
def function_one():
    while True:
        print("Function One is running.")

        responses = client2.simGetImages([airsim.ImageRequest("low_res", airsim.ImageType.Scene)])
        if responses:
            response = responses[0]
            img_rgb = cv2.imdecode(np.frombuffer(response.image_data_uint8, dtype=np.uint8), cv2.IMREAD_COLOR)
            #img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            #img_rgb = img1d.reshape(response.height, response.width, 3)
        if img_rgb is not None:
            # Resize if needed


            img_rgb_resized = cv2.resize(img_rgb, (1280, 1080))
            client2.processor = MediaProcessor()
            img_rgb_detected = client2.processor.process_video_frame(img_rgb_resized)
            # Write frame to video
            out.write(img_rgb_detected)
            #file_name = os.path.join('c:/Users/jholman/Documents/AirSim/Test/', f"image_{time.time()}.png")
            #cv2.imwrite(file_name, img_rgb_resized)
            print("image Processed")
        if stop_thread1:
            break


# Define the second function to run in a separate thread
# def function_two():
#    while True:
#        print("Function Two is running.")
#        time.sleep(1)
#        global stop_thread2
#        if stop_thread2:
#            break

thread_one = threading.Thread(target=function_one)

# thread_two = threading.Thread(target=function_two)
stop_thread1 = False
# stop_thread2 = False
# Start both threads


thread_one.start()
# thread_two.start()
print("Threads started.")

# Run code for flight
z = -10
print("make sure we are hovering at {} meters...".format(-z))
client.moveToZAsync(z, 1).join()

# see https://github.com/Microsoft/AirSim/wiki/moveOnPath-demo

# this method is async and we are not waiting for the result since we are passing timeout_sec=0.

print("flying on path...")
result = client.moveOnPathAsync([airsim.Vector3r(125,0,z),
                                airsim.Vector3r(125,-140,z),
                                airsim.Vector3r(0,-140,z),
                                airsim.Vector3r(0,0,z)],
                        5, 10000,
                        airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), 20, 1).join()
print("landing...")
client.landAsync().join()
print("disarming...")
client.armDisarm(False)
client.enableApiControl(False)
print("done.")

print("Waiting for Thread to stop")
print("Waiting for Thread to stop")
stop_thread1 = True
out.release()

# stop_thread2 = True
print("Functions should stop.")

client.reset()
