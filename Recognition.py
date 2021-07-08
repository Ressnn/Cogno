from deepface import DeepFace
import pandas as pd
from PIL import Image
import os
import numpy as np
import logging
import uuid
from playsound import playsound
import random
import pyaudio
import wave
import threading
from collections import deque



#models = ["VGG-Face", "Facenet", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

class FacialIdentifier():
    def __init__(self,dbpath="./Data/facebase"):
        """
        Constructor for the FacialIdentifier Class which handles the identification and addition of new faces.

        Parameters
        ----------
        dbpath : String
            The path to where the facebase is.

        Returns
        -------
        NoneType
            None.

        """
        self.dbpath = dbpath
    def add_face(self,face,name):
        """
        Adds a face to the facebase.

        Parameters
        ----------
        face : numpy.array
            A numpy array that contains the image data for a persons face
        name : sting
            The name to save a persons face into in the facebase

        Returns
        -------
        NoneType
            None.

        """

        try:
            os.mkdir(os.path.join(self.dbpath,name))
        except:
            pass

        imgface = Image.fromarray(face)
        imgface.save(os.path.join(self.dbpath,name,str(uuid.uuid4())+".jpg"))

    def find(self,face):
        """
        Finds all possible faces that a person could be mn

        Parameters
        ----------
        face : type
            Description of parameter `face`.

        Returns
        -------
        type
            Description of returned object.

        """
        return DeepFace.find(img_path=face,db_path="./Data/facebase",enforce_detection = False)

    def get_person(self,face,prob_threshold=.04):
        """Short summary.

        Parameters
        ----------
        face : type
            Description of parameter `face`.
        prob_threshold : type
            Description of parameter `prob_threshold`.

        Returns
        -------
        type
            Description of returned object.

        """
        connectors = self.find(face).to_numpy()
        if float(connectors[0,1])<=prob_threshold:
            return os.path.split(os.path.split(connectors[0,0])[0])[-1]
        else:
            logging.info("No suitable matches found")
            return -1

class AudioBuffer():
    def __init__(self,dbpath,seconds=3):
        """Short summary.

        Parameters
        ----------
        dbpath : type
            Description of parameter `dbpath`.
        seconds : type
            Description of parameter `seconds`.

        Returns
        -------
        type
            Description of returned object.

        """

        self.dbpath = dbpath
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = seconds

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        self.frames = deque()
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

        self.AudioThread = threading.Thread(target=self._read_loop, args=())
        self.AudioThread.start()

    def read(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        data = self.stream.read(self.CHUNK)
        self.frames.append(data)
        self.frames.popleft()

    def _read_loop(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        while True:
            self.read()

    def get(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        return self.frames

    def close(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def save(self,name):
        """Short summary.

        Parameters
        ----------
        name : type
            Description of parameter `name`.

        Returns
        -------
        type
            Description of returned object.

        """
        try:
            os.mkdir(os.path.join(self.dbpath,name))
        except:
            pass

        wf = wave.open(os.path.join(self.dbpath,name,str(uuid.uuid4())+".wav"), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(list(self.frames)))
        wf.close()
