from deepface import DeepFace
import pandas as pd
from PIL import Image
import os
import numpy as np
import logging
import uuid
import speech_recognition as sr
from playsound import playsound
import random
import pyaudio
import wave




#models = ["VGG-Face", "Facenet", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

class FacialIdentifier():
    def __init__(self,dbpath="./Data/facebase"):
        self.dbpath = dbpath
    def add_face(self,face,name):
        imgface = Image.fromarray(face)
        imgface.save(os.path.join(self.dbpath,name,str(uuid.uuid4())+".jpg"))

    def find(self,face):
        return DeepFace.find(img_path=face,db_path="./Data/facebase",enforce_detection = False)

    def get_person(self,face,prob_threshold=.04):
        connectors = self.find(face).to_numpy()
        if float(connectors[0,1])<=prob_threshold:
            return os.path.split(os.path.split(connectors[0,0])[0])[-1]
        else:
            logging.info("No suitable matches found")
            return -1

class AudioBuffer():
    def __init__(self,dbpath):
        self.dbpath = dbpath
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 5

        self.p = pyaudio.PyAudio()
        self.stream = p.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        self.frames = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            self.frames.append(data)

    def read(self):
        data = stream.read(self.CHUNK)
        self.frames.append(data)
        self.frames.pop(0)

    def get(self):
        return self.frames

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def save(self,dbpath,name):
        try:
            os.mkdir(os.path.join(self.dbpath,name))
        except:
            pass

        wf = wave.open(os.path.join(self.dbpath,name,str(uuid.uuid4())+".wav"), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

class SpeechRecognition():
    def __init__(self,dbpath="./Data/audiobase"):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.dbpath = dbpath
    def listen(self,phrases = ["my name is ", "i'm ", "i am "]):

        text,audio = self.get_sentence()

        if text == None:
            return None

        for phrase in phrases:
            start_name = text.find(phrase)
            if start_name == -1:
                continue

            start_name += len(phrase)

            end_name = text.find(' ', start_name)
            end_name = len(text) if end_name == -1 else end_name

            return text[start_name:end_name],audio
        return None

    def get_sentence(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return None,audio
        return text,audio

    def add_person(self,phrases=["my name is ", "i'm ", "i am "]):
        try:
            text,audio = self.listen(phrases=phrases)
        except:
            return None
        try:
            os.mkdir(os.path.join(self.dbpath,text))
        except:
            pass
        f = open(os.path.join(self.dbpath,text,str(uuid.uuid4())+".wav"), "wb")
        f.write(audio.get_wav_data())
        f.close()

        return text

    def add_audio(self,audio,name):
        try:
            os.mkdir(os.path.join(self.dbpath,name))
        except:
            pass
        f = open(os.path.join(self.dbpath,name,str(uuid.uuid4())+".wav"), "wb")
        f.write(audio.get_wav_data())
        f.close()
