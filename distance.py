import cv2 as cv
from cv2 import aruco
import numpy as np
import playsound
import threading
import time
import json

with open('C:/hackathon/program/DISTANCE-ESTIMATION/sound_output.json', 'r', encoding='utf-8') as file_json:
    data = json.load(file_json)

calib_data_path = "../calib_data/MultiMatrix.npz"

calib_data = np.load(calib_data_path)

print(calib_data.files)

cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

MARKER_SIZE = 8  # centimeters

sound_num = 0

marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

param_markers = aruco.DetectorParameters_create()

cap = cv.VideoCapture(0)

def output_sound(num):
    if num == 1:
        playsound.playsound('turn-left.mp3')
    else:
        playsound.playsound('turn-right.mp3')

def location_detect(num):

    if num > 10:
        output_sound(1)

    elif num < -10:
        output_sound(0)

    else:
        print("in the location")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(
        gray_frame, marker_dict, parameters=param_markers
    )
    if marker_corners:
        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(
            marker_corners, MARKER_SIZE, cam_mat, dist_coef
        )
        total_markers = range(0, marker_IDs.size)
        for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):
            cv.polylines(
                frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

            # Since there was mistake in calculating the distance approach point-outed in the Video Tutorial's comment
            # so I have rectified that mistake, I have test that out it increase the accuracy overall.
            # Calculating the distance

            distance = np.sqrt(
                tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2
            )
            # Draw the pose of the marker
            point = cv.drawFrameAxes(frame, cam_mat, dist_coef, rVec[i], tVec[i], 4, 4)
            cv.putText(
                frame,
                f"id: {ids[0]} Dist: {round(distance, 2)}",
                top_right,
                cv.FONT_HERSHEY_PLAIN,
                1.3,
                (0, 0, 255),
                2,
                cv.LINE_AA,
            )
            cv.putText(
                frame,
                f"x:{round(tVec[i][0][0],1)} y: {round(tVec[i][0][1],1)} ",
                bottom_right,
                cv.FONT_HERSHEY_PLAIN,
                1.0,
                (0, 0, 255),
                2,
                cv.LINE_AA,
            )
            # output sound

            # around_building
            if ids[0] == 0:
                for key in range(len(data)):
                    if data[key]['id'] <= 9:
                        print(data[key]['name'])

            # building_data
            if 1 <= ids[0] <= 3:
                print(data[ids[0]-1]['output'])

            # location_sound
            elif 10 <= ids[0] <= 40:
                location_detect(tVec[i][0][0])

            # danger_detect
            elif ids[0] > 40:
                for key in range(len(data)):
                    if ids[0] == data[key]['id']:
                        print(data[key]['output'])

            # emergency
            if round(distance, 2) < 35:
                print("help")

            #output sound
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()
