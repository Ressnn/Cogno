from deepface import DeepFace
import pandas as pd
from PIL import Image
import os
import numpy as np
import logging
models = ["VGG-Face", "Facenet", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

class FacialIdentifier():
    def __init__(self,dbpath="./Data/facebase"):
        self.dbpath = dbpath

    def add_face(self,face,name):
        imgface = Image.fromarray(face)
        imgface.save(os.path.join(self.dbpath))

    def find(self,face):
         return DeepFace.find(img_path=face,db_path="./Data/facebase",enforce_detection = False)

    def get_person(self,face,prob_threshold=.04):
        connectors = self.find(face).to_numpy()
        if float(connectors[0,1])<=prob_threshold:
            return os.path.split(os.path.split(connectors[0,0])[0])[-1]
        else:
            logging.info("No suitable matches found")
            return -1
F = FacialIdentifier()


image = Image.open(r"C:\Users\ASUS\Documents\Cogno\Data\Test\WIN_20210702_12_17_06_Pro.jpg")
narray = np.asarray(image)
#F.find(narray).to_numpy()
F.get_person(narray,prob_threshold=.3)
