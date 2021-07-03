from deepface import DeepFace
import pandas as pd
from PIL import Image
import os
import numpy as np
import logging
import uuid

models = ["VGG-Face", "Facenet", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

class FacialIdentifier():
    def __init__(self,dbpath="./Data/facebase"):
        self.dbpath = dbpath

    def add_face(self,face,name):
        directory = os.path.join(self.dbpath, name)
        os.makedirs(directory)

        imgface = Image.fromarray(face)
        imgface.save(os.path.join(directory, str(uuid.uuid4()) + ".jpg"))

    def find(self,face):
         return DeepFace.find(img_path=face,db_path="./Data/facebase",enforce_detection = False)

    def get_person(self,face,prob_threshold=.04):
        connectors = self.find(face).to_numpy()
        if float(connectors[0,1])<=prob_threshold:
            return os.path.split(os.path.split(connectors[0,0])[0])[-1]
        else:
            logging.info("No suitable matches found")
            return -1
