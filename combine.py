import cv2 as cv
from cv2 import aruco
import numpy as np
import threading
import time
import json
import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound


with open('sound_output.json', 'r', encoding='utf-8') as file_json:
    data = json.load(file_json)
 
calib_data_path = "MultiMatrix.npz"
 
calib_data = np.load(calib_data_path)
 
print(calib_data.files)
 
cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]
 
MARKER_SIZE = 8  # centimeters
 
marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
 
param_markers = aruco.DetectorParameters_create()
 
danger_sound = False

sum_t=0.0 

cap = cv.VideoCapture(0)
 
def output_sound(num):
    if num == 1:
        playsound('right.mp3')
        #time.sleep(1)
    else:
        playsound('left.mp3')
        # time.sleep(1)
 
def location_detect(num):
 
    if num > 10:
        output_sound(1)
 
    elif num < -10:
        output_sound(0)
 
    else:
        print("in the location")

def sound_load():
    #first tag
    mytext=''
    for key in range(len(data)):
        if data[key]['id'] <= 9:
            mytext = mytext + data[key]['name']
            audio = gTTS(text=mytext, lang="en", slow=False)
            audio.save("building.mp3")
    
    #second tag
    mytext=''
    for i in range(1,3):
        mytext = data[i-1]['output']
        audio = gTTS(text=mytext, lang="zh-tw", slow=False)
        audio.save("all_room"+str(i)+".mp3")

    #third tag
    mytext=''
    for key in range(len(data)):
        if 41<= data[key]['id'] <=43:
            mytext = data[key]['output']
            audio = gTTS(text=mytext, lang="zh-tw", slow=False)
            audio.save("danger"+str(data[key]['id'])+".mp3")
    
    #forth
    mytext=''
    for key in range(len(data)):
        if 10<= data[key]['id'] <=39:
            mytext = data[key]['output']
            audio = gTTS(text=mytext, lang="zh-tw", slow=False)
            audio.save("room"+str(data[key]['id'])+".mp3")

def SpeechToText():
    r = sr.Recognizer()   #Speech recognition
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        if(r.recognize_google(audio, language = 'zh-tw')=='圖書館'):
            mytext = "圖書館在你後面"
            audio = gTTS(text=mytext, lang="zh", slow=False)
            audio.save("example.mp3")
            os.system("start example.mp3")
        elif(r.recognize_google(audio, language = 'zh-tw')=='廁所'):
            mytext = "the restroom is above you haha"
            audio = gTTS(text=mytext, lang="en", slow=False)
            audio.save("example.mp3")
            os.system("start example.mp3")
        return 1
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand what the you say")
        return 0
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return 0 


sound_load()
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

            # emergency
            if round(distance, 2) < 35:
                sum_t+=1
                if sum_t > 200:
                    sum_t=0.0 
                    playsound("help.mp3")
            else:
                sum_t=0.0
                
            
            # around_building
            if ids[0] == 0:
                playsound("building.mp3")
                time.sleep(1)
                while(1):
                    again=SpeechToText()
                    if(again):
                        break
                    print(again)
                 # print(data[key]['name'])
                 
 
            # building_data
            elif 1 <= ids[0] <= 3:
                if os.path.isfile("./all_room.mp3"):
                    playsound("all_room.mp3")
                # print(data[ids[0]-1]['output'])
            
            #room_location
            elif 10 <= ids[0] <=39:
                if os.path.isfile(str("./room"+str(ids[0])+".mp3")):
                    location_detect(tVec[i][0][0])
                    if round(distance, 2) < 50:
                        playsound("room"+str(ids[0])+".mp3")

            # location_sound
            elif ids[0] == 40:
                location_detect(tVec[i][0][0])
 
            # danger_detect 1~3
            elif 41<= ids[0] <= 43:
                playsound("danger"+str(ids[0])+".mp3")
                 # print(data[key]['output'])

            #output sound
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()