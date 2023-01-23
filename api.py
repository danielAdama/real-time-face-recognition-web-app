from quart import Quart, request, jsonify
from quart_cors import cors
import numpy as np
import pickle
from Utilities import process
from face_verification.face_verify import FaceRecognition
import cv2
import imutils
import logging
import time
import argparse
from config import config

app = Quart(__name__)
app.config['Flask_DEBUG'] = "development"
handle = "my-api"
cors(app)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.NOTSET, datefmt='%d-%b-%y %H:%M:%S')
_logger = logging.getLogger(handle)

with open('encodings', 'rb') as f:
    data = pickle.load(f)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Face Recognizer Api exposing hog model")
    parser.add_argument("-p", "--port", default=8080, type=int, help="port number")
    args = parser.parse_args()
    app.run(host='0.0.0.0', debug=False, port=args.port)