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
from sms import sms_out


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

location_name = []

path = "sound/"

cap = cv.VideoCapture(0)
 
def output_sound(num):
    if num == 1:
        playsound(path+'right.mp3')
        #time.sleep(1)
    else:
        playsound(path+'left.mp3')
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
    mytext= ''
    for key in range(len(data)):
        name = ''
        if data[key]['id'] <= 9:
            # all_building
            mytext = mytext + data[key]['name']

            # build_name
            # print(data[key]['location'])
            name = data[key]['location']
            audio = gTTS(text= name, lang="zh-tw", slow=False)
            audio.save("building"+str(data[key]['id'])+".mp3")
            # print("building"+str(data[key]['id'])+".mp3")
            
        
    # all_building
    audio = gTTS(text=mytext, lang="zh-tw", slow=False)
    audio.save("all_building.mp3")
    
    #second tag
    mytext=''
    for i in range(1,4):
        mytext = data[i-1]['output']
        audio = gTTS(text=mytext, lang="zh-tw", slow=False)
        audio.save(path+"all_room"+str(i)+".mp3")

    #third tag
    mytext=''
    for key in range(len(data)):
        if 41<= data[key]['id'] <=43:
            mytext = data[key]['output']
            audio = gTTS(text=mytext, lang="zh-tw", slow=False)
            audio.save(path+"danger"+str(data[key]['id'])+".mp3")
    
    #forth
    mytext=''
    for key in range(len(data)):
        if 10<= data[key]['id'] <=39:
            mytext = data[key]['output']
            audio = gTTS(text=mytext, lang="zh-tw", slow=False)
            audio.save(path+"room"+str(data[key]['id'])+".mp3")
    

    #fifth
    mytext = '三公尺'
    audio = gTTS(text=mytext, lang="zh-tw", slow=False)
    audio.save(path+"3m.mp3")

    mytext = '一公尺'
    audio = gTTS(text=mytext, lang="zh-tw", slow=False)
    audio.save(path+"1m.mp3")

    #sixth
    mytext = '左'
    audio = gTTS(text=mytext, lang="zh-tw", slow=False)
    audio.save(path+"left.mp3")

    mytext = '右'
    audio = gTTS(text=mytext, lang="zh-tw", slow=False)
    audio.save(path+"right.mp3")


    
def SpeechToText():
    r = sr.Recognizer()   #Speech recognition
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        if(r.recognize_google(audio, language = 'zh-tw')=='圖書館'):
            os.system("start building1.mp3")
        elif(r.recognize_google(audio, language = 'zh-tw')=='博物館'):
            os.system("start building2.mp3")
        elif(r.recognize_google(audio, language = 'zh-tw')=='體育館'):
            os.system("start building3.mp3")
        return 1
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand what the you say")
        return 0
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return 0 


#type python catchErrorSpeech.py to execute

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
                f"x:{round(tVec[i][0][0]-6,1)} y: {round(tVec[i][0][1],1)} ",
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
                    sms_out("我目前可能受傷了，請試圖聯絡我")
                    playsound(path+"help.mp3")
            else:
                sum_t=0.0
                
            
            # around_building
            if ids[0] == 0:
                os.system("start all_building.mp3")
                time.sleep(3)
                while(1):
                    again=SpeechToText()
                    if(again):
                        break
                    print(again)
            # print(data[key]['name'])
 
            # building_data
            elif 1 <= ids[0] <= 3:
                if os.path.isfile(path+"all_room.mp3"):
                    playsound(path+"all_room"+str(ids[0])+".mp3")
                # print(data[ids[0]-1]['output'])
            
            #room_location
            elif 10 <= ids[0] <=39:
                if os.path.isfile(str(path+"room"+str(ids[0])+".mp3")):
                    location_detect(tVec[i][0][0])
                    if round(distance, 2) < 50:
                        playsound(path+"room"+str(ids[0])+".mp3")

                    elif round(distance, 2) < 100:
                        playsound(path+"1m.mp3")

                    elif round(distance, 2) < 300:
                        playsound(path+"3m.mp3")

            # location_sound
            elif ids[0] == 40:
                location_detect(tVec[i][0][0])

            # danger_detect 1~3
            elif 41 <= ids[0] <= 43:
                playsound(path+"danger"+str(ids[0])+".mp3")
                 # print(data[key]['output'])

            #output sound
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()