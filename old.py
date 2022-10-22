import speech_recognition as sr
from gtts import gTTS
import os

r = sr.Recognizer()
mic = sr.Microphone()
with mic as source:
    audio = r.listen(source)
print(r.recognize_google(audio))
hear_val = r.recognize_google(audio)

if(hear_val=='hello I am human'):
    mytext = "Hi, i am stupid robot"
    audio = gTTS(text=mytext, lang="en", slow=False)
    audio.save("example.mp3")
    os.system("start example.mp3")
elif(hear_val=='are you stupid'):
    mytext = "no I am not"
    audio = gTTS(text=mytext, lang="en", slow=False)
    audio.save("example.mp3")
    os.system("start example.mp3")
else:
    print("fuck you")