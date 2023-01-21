from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
from face_verification.face_verify import FaceRecognition
import cv2
import os
from PIL import Image
import imutils
import io
import time
import base64
from config import config
import json

app = Flask(__name__)
CORS(app)
with open('encodings', 'rb') as f:
    data = pickle.load(f)

def video_stream():
    webcam = cv2.VideoCapture(0)
    time.sleep(2.0)
    if (webcam.isOpened() == False):
        print('\nUnable to read camera feed')

    while True:
        success, frame = webcam.read()
        if success == True:
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 500px (to speedup processing) 
            # rgb = cv2.cvtColor(frame, config.COLOR)
            # rgb = imutils.resize(frame, 500)
            # (h, w) = frame.shape[:2]
            # r = w / rgb.shape[1]
            rgb = cv2.cvtColor(frame, config.COLOR)
            rgb = imutils.resize(frame, 500)
            (h, w) = frame.shape[:2]
            r = w / rgb.shape[1]
            
            fv = FaceRecognition(rgb, data=data)
            boxes, names, accs = fv.faceAuth()

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
            ret, buffer = cv2.imencode(".jpg", frame)
            yield(
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'+ buffer.tobytes() +
                b'\r\n\r\n'
                )

            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            break
    webcam.release()
    cv2.destroyAllWindows()

def readb64(data):
    img_arr = np.frombuffer(base64.b64decode(data), np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return img

@app.route('/api/v1/verify', methods = ["POST"])
def verify():
    try:
        json_data = request.get_json()
        try:
            if not json_data:
                return {
                    "message": "Please make sure your camera is ON",
                    "data": None,
                    "error": "Bad request"
                }, config.HTTP_400_BAD_REQUEST
            
            time.sleep(0.02)
            frame = readb64(json_data)
            rgb = cv2.cvtColor(frame, config.COLOR)
            rgb = imutils.resize(frame, 648)
            (h, w) = frame.shape[:2]
            r = w / rgb.shape[1]
            
            fv = FaceRecognition(rgb, data=data, model='hog')
            try:
                boxes, names, accs, encodings = fv.faceAuth()
                if len(encodings) != 0:
                    for ((top, right, bottom, left), name) in zip(boxes, names):
                        top, right, bottom, left = (int(top*r)), (int(right*r)), (int(bottom*r)), (int(left*r))
                        if name !='Unknown':
                            for acc in accs:
                                print(name, acc)
                        print(name)
                    return {
                        ##"detections":json.loads(name),
                        "messsage":"Successfully processed image"
                    }, config.HTTP_200_OK
            except:
                return {
                    "error":"Error processing frame! No face found",
                    "message":"No face Detected"
                }, config.HTTP_404_NOT_FOUND

        except Exception as ex:
            return {
                "error":"Something went wrong",
                "message":str(ex)
            }, config.HTTP_500_INTERNAL_SERVER_ERROR

    except Exception as ex:
            return {
                "error":"The data is not in json format",
                "message":str(ex)
            }, config.HTTP_404_NOT_FOUND

if __name__ == '__main__':
    app.run()