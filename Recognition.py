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
        Finds all possible faces that a person could be

        Parameters
        ----------
        face : numpy.array
            A person's face in an image of proportions (w,h,3)

        Returns
        -------
        pandas.Dataframe
            A pandas dataframe with all of the possible faces in the frame

        """
        return DeepFace.find(img_path=face,db_path="./Data/facebase",enforce_detection = False)

    def get_person(self,face,prob_threshold=.04):
        """
        Gets the person most present in the frame

        Parameters
        ----------
        face : np.array
            numpy array of an image with a face in it
        prob_threshold : float
            the cosine threshold to say that a person is someone that was recognized

        Returns
        -------
        String
            Returns the string of the person's name

        """
        connectors = self.find(face).to_numpy()
        if float(connectors[0,1])<=prob_threshold:
            return os.path.split(os.path.split(connectors[0,0])[0])[-1]
        else:
            logging.info("No suitable matches found")
            return -1

class AudioBuffer():
    def __init__(self,dbpath,seconds=3):
        """
        An audiobuffer that keeps the last few seconds of audio in memory

        Parameters
        ----------
        dbpath : String
            The path to the audiobase.
        seconds : float or int
            The the amount of time to keep in memory

        Returns
        -------
        NoneType
            None

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
        """
        Reads another moment of the audio and adds it to the buffer whiled popleft() in the last second

        Returns
        -------
        NoneType
            None

        """
        data = self.stream.read(self.CHUNK)
        self.frames.append(data)
        self.frames.popleft()

    def _read_loop(self):
        """
        Loops the read function

        Returns
        -------
        NoneType
            None

        """
        while True:
            self.read()

    def get(self):
        """
        Gets the last few seconds of the audiobuffer

        Returns
        -------
        deque
            A deque with raw audio data from PyAudio

        """
        return self.frames

    def close(self):
        """
        Closes the pyaudio stream and stops recording

        Returns
        -------
        NoneType
            None

        """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def save(self,name):
        """
        Saves the audiostream to a file under the audiobase with a folder called "name"

        Parameters
        ----------
        name : str
            Name to save the folder under in the audiobase

        Returns
        -------
        NoneType
            None

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
