import setup_path
import airsim
import datetime
import sys
import time
import pprint
import cv2
import os
import numpy as np
import time
from airsimgeo import AirSimGeoClient
print("""This is piece of code to capture set of images with attached text file with 
text file with attached GPS corodinates with height and heading for learning models utilizing 
geolocation based on map utitilites provided by Unreal Plugin
Originital idea was to gest set of images from different heights to train and test geolocation of a drone
""")

# on linux please adjust path to any folder you want it to be saved to I'm using it on windows so far
# adjust line underneath to match your file structure
output_folder = "c:/Users/jholman/Documents/AirSim/Test_geo/"
#output_folder = "/home/username/AirSim/Test_geo/"

client = airsim.VehicleClient()
client.confirmConnection()

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)


def capture_images_and_gps():
    framecounter = 1
    # Infinite loop to continuously update the image in the same window
    while framecounter < 60:
        # Obtain images from AirSim
        print("GetPictures")
        responses = client.simGetImages([airsim.ImageRequest("high_res", airsim.ImageType.Scene)])
        for response in responses:
            img_rgb = cv2.imdecode(np.frombuffer(response.image_data_uint8, dtype=np.uint8), cv2.IMREAD_COLOR)
            if response is not None:
                print("GetPictures3")
                # Get the image and save it to numbered file
                image_path = os.path.join(output_folder, f"{framecounter}_image.png")
                cv2.imwrite(image_path, img_rgb)

                # Get Actual GPS position and altitude and write it to file with same number as picture taken
                gpsfile_path = os.path.join(output_folder, f"{framecounter}_gps.txt")
                gps_data = client.getGpsData()
                yaw = airsim.to_eularian_angles(state.kinematics_estimated.orientation)[2] * 180.0 / 3.14159  # Convert radians to degrees
                with open(gpsfile_path, "w") as file:
                    file.write(
                    "Latitude:" + str(gps_data.gnss.geo_point.latitude) + " , " +
                    "Longitude:" + str(gps_data.gnss.geo_point.longitude) + " , " +
                    "Altitude:" + str(gps_data.gnss.geo_point.altitude) + " , " +
                    str("Heading: {}".format(yaw))
                    )
                cv2.imwrite(image_path, img_rgb)
                # add framecounter and wait for 4 seconds
                print("PicturesTaken " + str(framecounter))
                framecounter += 1
                time.sleep(4)


print("arming the drone...")
client.armDisarm(True)
state = client.getMultirotorState()

print("taking off...")
client.takeoffAsync().join()

# AirSim uses NED coordinates so negative axis is up.
# z of -5 is 5 meters above the original launch point.
z = -5
print("make sure we are hovering at {} meters...".format(-z))
client.moveToZAsync(z, 1).join()

# see https://github.com/Microsoft/AirSim/wiki/moveOnPath-demo

# this method is async and we are not waiting for the result since we are passing timeout_sec=0.
print("flying on path...")
client.moveToPositionAsync(24, -90, -15, 6).join()
client.moveToPositionAsync(24, -190, -1500, 3)
capture_images_and_gps()
print("move to position ended")


# drone will over-shoot so we bring it back to the start point before landing.
client.moveToPositionAsync(0,0,z,1).join()
print("landing...")
client.landAsync().join()
print("disarming...")
client.armDisarm(False)
client.enableApiControl(False)
print("done.")
