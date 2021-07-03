import speech_recognition as sr
from playsound import playsound
import random
import os

KEY_PHRASES = ["my name is ", "i'm ", "i am "]

def notify_name_captured():
    if random.randint(0, 1) == 0:
        playsound('speech/dababy.mp3')
    else:
        playsound('speech/ha.mp3')

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
    
    def listen(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
    
        try:
            text = self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return None

        for phrase in KEY_PHRASES:
            start_name = text.find(phrase)
            if start_name == -1:
                continue
            
            start_name += len(phrase)

            end_name = text.find(' ', start_name)
            end_name = len(text) if end_name == -1 else end_name
            
            notify_name_captured()

            return text[start_name:end_name]

        return None
