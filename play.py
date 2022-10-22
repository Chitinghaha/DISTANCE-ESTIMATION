import speech_recognition as sr
from gtts import gTTS
import os

def SpeechToText():
    print(1)
    r = sr.Recognizer()   #Speech recognition
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        if(r.recognize_google(audio, language = 'zh-tw')=='你好'):
            mytext = "誠宜開張聖聽，以光先帝遺德，恢弘志士之氣，不宜妄自菲薄，引喻失義，以塞忠諫之路也"
            audio = gTTS(text=mytext, lang="zh", slow=False)
            audio.save("example.mp3")
            os.system("start example.mp3")
        elif(r.recognize_google(audio, language = 'zh-tw')=='手機'):
            mytext = "no I am not"
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

while(1):
    again = SpeechToText()
    if(again):
        break
    print(again)

#type python catchErrorSpeech.py to execute