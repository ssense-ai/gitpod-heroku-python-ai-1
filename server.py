import threading
import os
import sys
import time
import datetime
import io
import re
import base64
import uuid
import queue
import logging
import traceback

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import pickle

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS, cross_origin

#Queue for process prediction
prediction_queue = queue.Queue()
#Dict for result OCR
result_dict = dict()

def predict_worker():
    while True:
        # process predict request
        if not prediction_queue.empty():
            predict_request = prediction_queue.get()
            print('found queue')
            if 'id' in predict_request:
                print('process:' + predict_request['id'])
                try:
                    '''
                    extractedInformation = pytesseract.image_to_string(Image.open(io.BytesIO(ocr_request['image'])),
                                                                       lang=ocr_request['lang'], 
                                                                       config=ocr_request['config'])
                    '''
                    result_dict[predict_request['id']] = {'result': extractedInformation,
                                                     'time': datetime.datetime.now(),
                                                     'error': None }
                    print('success:' + predict_request['id'])
                except Exception as e:
                    result_dict[predict_request['id']] = {'result': None,
                                                     'time': datetime.datetime.now(),
                                                     'error': traceback.format_exc() }
                    print('failure:' + predict_request['id'])
        # clean up old results
        for key in list(result_dict.keys()):
            result_time = result_dict[key]['time']
            if (datetime.datetime.now() - result_time).total_seconds() > 300:
                del result_dict[key]
                print('result of request id[' + key + '] now removed')

        time.sleep(0.1)

prediction_thread = threading.Thread(target=predict_worker)
prediction_thread.start()


app = Flask(__name__, static_folder='node_modules')
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
CORS(app)

@app.route('/')
def root_html():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)),'predict.html')

@app.route('/predict.js')
def root_js():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)),'predict.js')

# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, threaded=True)