import numpy as np
import pickle
import face_recognition
import cv2
import os
from config import config


knownEncodings = []
knownNames = []

for name in os.listdir(config.KNOWN_PATH):
    for filename in os.listdir(os.path.join(config.KNOWN_PATH,name)):
        print(f"Processing {name}'s face!")
        image = cv2.imread(os.path.join(config.KNOWN_PATH,name,filename))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect the (x, y) co-ordinate of face(s)
        boxes = face_recognition.face_locations(image, model=config.MODEL) #cnn

        encodings = face_recognition.face_encodings(image, boxes)
        # Loop over the encodings and add their name(s) and face(s), respectively to the database
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

print('\nSuccessfully Serialized Face(s) into the Database'+"..."*3)
data = {"encodings": knownEncodings, "names": knownNames}
with open("encodings", "wb") as f:
    f.write(pickle.dumps(data))
    f.close()