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
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
CORS(app)

@app.route('/')
def root_html():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)),'predict.html')

@app.route('/predict.js')
def root_js():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)),'predict.js')