from Utilities.db import Database
import face_recognition
import cv2
import os
import datetime
from config import config
import json


db = Database(config.CONNECTIONSTRING, config.DATABASE, "UserEncoding")
output = {}
counter = 0

try:
    for name in os.listdir(config.KNOWN_PATH):
        for filename in os.listdir(os.path.join(config.KNOWN_PATH,name)):
            counter += 1
            #print(f"Processing {name}'s face!")
            image = cv2.imread(os.path.join(config.KNOWN_PATH,name,filename))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(image, model=config.MODEL) #cnn

            if len(boxes) > 0:
                encodings = face_recognition.face_encodings(image, boxes)
                # Reset the counter for new faces
                if (output.get('Name') is not None):
                    if (output['Name'] != name):
                        counter = 1
                # Loop over the encodings and add their name(s) and face(s), respectively to the database
                # for encoding in encodings:
                for i in range(len(encodings)):
                    data = {
                        "Name":name,
                        "FaceId": counter,
                        "TimeCreated":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "Encoding": json.dumps(encodings[i])
                    }
                    output['Name'] = name
                    db.connected().UserEncoding.insert_one(
                        data
                    )
    print('\nSuccessfully Serialized Face(s) into the Database'+"..."*3)
except:
    pass