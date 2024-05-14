import setup_path
import airsim
import datetime
import sys
import time
import pprint
import cv2
import os
import numpy as np
print("""This script is designed to fly on the streets of the Neighborhood environment
and assumes the unreal position of the drone is [160, -1500, 120].""")

output_folder = "c:/Users/jholman/Documents/AirSim/Test/"


client = airsim.VehicleClient()
client.confirmConnection()
framecounter = 1


client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

if client.armDisarm is False:

    print("arming the drone...")
    client.armDisarm(True)

    state = client.getMultirotorState()
    if state.landed_state == airsim.LandedState.Landed:
        print("taking off...")
        client.takeoffAsync().join()
    else:
        client.hoverAsync().join()

    time.sleep(1)

    state = client.getMultirotorState()
    if state.landed_state == airsim.LandedState.Landed:
        print("take off failed...")
        sys.exit(1)

    # AirSim uses NED coordinates so negative axis is up.
    # z of -5 is 5 meters above the original launch point.

    z = -5
    print("make sure we are hovering at {} meters...".format(-z))
    client.moveToZAsync(z, 1).join()

# see https://github.com/Microsoft/AirSim/wiki/moveOnPath-demo

# this method is async and we are not waiting for the result since we are passing timeout_sec=0.

print("flying on path...")

client.moveToPositionAsync(-10, 10, -10, 5).join()

client.hoverAsync().join()

state = client.getMultirotorState()

print("finished")

while(framecounter <= 10):
    print("finished1")
    # responses = client.simGetImages([airsim.ImageRequest("high_res", airsim.ImageType.Scene, False, False)])
    # print("finished2")
    #
    #
    # # image = responses[0].image_data_uint8
    #
    # print("High resolution image captured.")
    # img1d = np.fromstring(responses.image_data_uint8, dtype=np.uint8) # get numpy array
    # img_rgb = img1d.reshape(responses.height, responses.width, 3) # reshape array to 4 channel image array H X W X 3
    # # img_rgb = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
    # # print(img_rgb)
    # image_path = os.path.join(output_folder, f"image_{framecounter}.png")
    # # print(image_path)
    # cv2.imwrite(image_path, img_rgb)

    response = client.simGetImages([airsim.ImageRequest("high_res", airsim.ImageType.Scene, False, False)])
    # Decode the image data
    img_rgb = cv2.imdecode(airsim.string_to_uint8_array(response.image_data_uint8), cv2.IMREAD_COLOR)
    print(img_rgb)
    # Check if decoding was successful
    if img_rgb is not None:
        # Display the image in a separate window
        cv2.imshow(f"Image {idx}", img_rgb)

# Wait for a key press to close the windows
cv2.waitKey(0)
cv2.destroyAllWindows()
    # for idx, response in enumerate(responses):
    #     image = response.image_data_uint8
    #     img_rgb = cv2.imdecode(airsim.string_to_uint8_array(image), cv2.IMREAD_COLOR)
    #
    #     if img_rgb is None:
    #         print(f"Failed to decode image for response {idx}. Skipping.")
    #         continue
    #     #image_path = os.path.join(output_folder, f"image_{framecounter}_{idx}.png")
    #     #cv2.imwrite(image_path, img_rgb)
    #     print(framecounter)
    #     framecounter += 1
    #     print(img_rgb.shape)
    #     cv2.imshow("AirSim Image", img_rgb)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

# drone will over-shoot so we bring it back to the start point before landing.
client.moveToPositionAsync(0,0,z,1).join()
print("landing...")
client.landAsync().join()
print("disarming...")
client.armDisarm(False)
client.enableApiControl(False)
print("done.")
