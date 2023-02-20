from quart import Quart, request, jsonify
from quart_cors import cors
import numpy as np
import face_recognition
import datetime
from Utilities import process
from face_verification.face_verify import FaceRecognition
import cv2
import imutils
import logging
from Utilities.db import Database
import json
import argparse
from config import config


app = Quart(__name__)
app.config['Flask_DEBUG'] = "development"
handle = "my-api"
cors(app)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.NOTSET, datefmt='%d-%b-%y %H:%M:%S')
_logger = logging.getLogger(handle)

db = Database(config.CONNECTIONSTRING, config.DATABASE, "UserEncoding")
data = db.processed_data()
faceRecog = FaceRecognition(data=data, model='hog')


@app.route('/api/v1/verify', methods = ["POST"])
async def verify():
    try:
        json_data = await request.get_json()
        try:
            if not json_data:
                _logger.warning("API VERIFY > please connect your camera")
                return {
                    "BaseResponse":{
                            "Status":False,
                            "Message": "Please make sure your camera is ON",
                            "Data": None,
                        },
                    "Error": "Bad request"
                }, config.HTTP_400_BAD_REQUEST
            
            frame = process.readb64(json_data)
            rgb = cv2.cvtColor(frame, config.COLOR)
            rgb = imutils.resize(frame, 440)
            (h, w) = frame.shape[:2]
            r = w / rgb.shape[1]
            
            try:
                boxes, names, accs, encodings = faceRecog.faceAuth(rgb)
                if len(encodings) != 0:
                    for ((top, right, bottom, left), name) in zip(boxes, names):
                        top, right, bottom, left = (int(top*r)), (int(right*r)), (int(bottom*r)), (int(left*r))
                        if name !='Unknown':
                            for acc in accs:
                                _logger.debug(f"API VERIFY > name: {name}, accuracy: {acc}")
                        else:
                            accs = 0
                            _logger.debug(f"API VERIFY > name: {name}, accuracy: {accs}")
                    return {
                        "BaseResponse":{
                            "Status":True,
                            "Messsage":"Operation successfully"
                        },
                        "Detections": {
                            "Label":name,
                            "Confidence":acc,
                            "Top":top,
                            "Right":right,
                            "Left":left,
                            "Bottom":bottom
                        },
                    }, config.HTTP_200_OK
            except Exception as ex:
                _logger.warning(f"API VERIFY > No face found")
                return {
                    "BaseResponse":{
                            "Status":False,
                            "Message":str(ex)
                        },
                    "Error":"Error processing frame! No face found"
                }, config.HTTP_404_NOT_FOUND

        except Exception as ex:
            _logger.warning(f"API VERIFY > APPLICATION ERROR while recognizing face")
            return {
                "BaseResponse":{
                            "Status":False,
                            "Message":str(ex)
                        },
                "Error":"Something went wrong",
            }, config.HTTP_500_INTERNAL_SERVER_ERROR

    except Exception as ex:
            _logger.warning(f"API VERIFY > The data is not in json format")
            return {
                "BaseResponse":{
                            "Status":False,
                            "Message":str(ex)
                        },
                "Error":"The data is not in json format",
            }, config.HTTP_404_NOT_FOUND

@app.route('/api/v1/train', methods=["POST"])
async def train():
    json_data = await request.get_json()
    try:
        if not json_data:
            _logger.warning("API VERIFY > please connect your camera")
            return {
                "BaseResponse":{
                        "Status":False,
                        "Message": "Please make sure your camera is ON",
                        "Data": None,
                    },
                "Error": "Bad request"
            }, config.HTTP_400_BAD_REQUEST

        frame = process.readb64(json_data['image'])
        boxes = face_recognition.face_locations(frame, model="hog")
        encoding = face_recognition.face_encodings(frame, boxes)[0]
        db.connected().UserEncoding.insert_one({
            "Name":json_data['name'],
            "TimeCreated":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Encoding": json.dumps(encoding.tolist())
        })
        return {
            "BaseResponse":{
                "Status":True,
                "Messsage":"Operation successfully"
            },
            "Detections": {
                "Name":json_data['name'],
                "Image":json_data['image'],
                "TimeCreated":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ##"Encoding": json.dumps(encoding)
            },
        }, config.HTTP_200_OK

    except Exception as ex:
        _logger.warning(f"API VERIFY > APPLICATION ERROR while recognizing face")
        return {
            "BaseResponse":{
                        "Status":False,
                        "Message":str(ex)
                    },
            "Error":"Something went wrong",
        }, config.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Face Recognizer Api exposing hog model")
    parser.add_argument("-p", "--port", default=8080, type=int, help="port number")
    args = parser.parse_args()
    app.run(host='0.0.0.0', debug=False, port=args.port)