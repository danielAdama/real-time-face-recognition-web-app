import numpy as np
import pickle
from face_verification.face_verify import FaceRecognition
import cv2
import os
import imutils
from Utilities.db import Database
import time
from config import config



db = Database(config.CONNECTIONSTRING, config.DATABASE, "UserEncoding")
data = db.processed_data()
faceRecog = FaceRecognition(data=data)

webcam = cv2.VideoCapture(0)
time.sleep(2.0)
if (webcam.isOpened() == False):
    print('\nUnable to read camera feed')


while True:
    success, frame = webcam.read()
    if success == True:
        # convert the input frame from BGR to RGB then resize it to have
        # a width of 500px (to speedup processing) 
        rgb = cv2.cvtColor(frame, config.COLOR)
        rgb = imutils.resize(frame, 500)
        (h, w) = frame.shape[:2]
        r = w / rgb.shape[1]
        
        try:
            boxes, names, accs, encodings = faceRecog.faceAuth(rgb)
            if len(encodings) != 0:
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    top, right, bottom, left = (int(top*r)), (int(right*r)), (int(bottom*r)), (int(left*r))

                    x = top - 15 if top - 15 > 15 else top + 15
                    if name=='Unknown':
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.rectangle(frame, (left, bottom + 25), (right, bottom), (0, 0, 255), cv2.FILLED)
                        cv2.putText(frame, name, (left+30, bottom+20), config.FONT, 0.5, 
                        (255, 255, 255), 2)
                    else:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        for acc in accs:
                            # Status box
                            cv2.rectangle(frame, (left, bottom + 25), (right, bottom), (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame, f"{name} {acc*100:.2f}%", (left+30, bottom+20), config.FONT, 0.5, 
                            (255, 255, 255), 2)
        except:
            print("No face detected")

        cv2.imshow('Live', frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
    else:
        break

webcam.release()
cv2.destroyAllWindows()