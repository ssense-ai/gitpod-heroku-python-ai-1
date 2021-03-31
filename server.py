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