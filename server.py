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
            if 'id' in predict_request and 'data' in predict_request:
                print('process:' + predict_request['id'])
                try:
                    prediction_result = predict(predict_request['data'])
                    result_dict[predict_request['id']] = {'result': prediction_result.to_csv(index=False),
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

#model読み込み
with open('lgb_model.pickle', mode='rb') as fp:
    model = pickle.load(fp)

def predict(test_data):
    #データ読み込み
    df_test = None
    if test_data is None:
        df_test = pd.read_csv("test.csv")
    else:
        df_test = pd.read_csv(io.StringIO(test_data))

    df_test.index = df_test["Id"]
    df_test.drop("Id", axis = 1, inplace = True)
    df_test = pd.get_dummies(df_test, drop_first=True)

    #予測
    prediction_LG = model.predict(df_test, predict_disable_shape_check = True)

    #小数を丸めている
    prediction_LG = np.round(prediction_LG)
    results = pd.DataFrame({"id": df_test.index, "SalePrice": prediction_LG})

    return results

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

@app.route('/default_data')
def default_data():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)),'test.csv')

@app.route('/predict', methods=['POST'])
@cross_origin(origin='*')
def process_predict():
    try:
        data = request.get_json()['data']
        predict_request_id = 'predict_id-' + str(uuid.uuid4())

        print('request id:' + predict_request_id + ' created')

        prediction_queue.put({'id': predict_request_id,
                              'data': data})

        return jsonify({'status': 'success',
                        'requestid': predict_request_id})
    except Exception as e:
        return jsonify({'status': 'error',
                        'requestid': None})  

@app.route('/result')
@cross_origin(origin='*')
def process_result():
    id = request.args['requestid']
    if id in result_dict:
        if result_dict[id]['result'] is not None:
            return jsonify({'status': 'success',
                        'message': '',
                        'result': result_dict[id]['result']})
        else:
            return jsonify({'status': 'error',
                        'message': result_dict[id]['error'],
                        'result': None})
    else:
            return jsonify({'status': 'not found'})


# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, threaded=True)