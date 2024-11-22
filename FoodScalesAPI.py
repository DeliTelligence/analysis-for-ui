# https://github.com/lucapinello/pydecentscale
# Used Open Source library here

# https://chatgpt.com
# prompt 'How to build an API service in python using flask library'
# prompt 'How to make service thread safe scales cant find the scale when a second request to activate is sent'

from flask import Flask, jsonify, request
import asyncio
import threading
from pydecentscale import DecentScale

app = Flask(__name__)

ds = DecentScale()
weight_lock = threading.Lock()
operation_lock = threading.Lock()
latest_weight = None

def background_weight_reader():
    global latest_weight
    while ds.connected:
        with weight_lock:
            if ds.weight is not None:
                latest_weight = ds.weight
        asyncio.run(asyncio.sleep(0.1))

@app.route('/connect', methods=['POST'])
def connect():
    with operation_lock:
        if not ds.connected:
            connected = ds.auto_connect()
            if connected:
                return jsonify({"status": "Connected to Decent Scale"}), 200
            else:
                return jsonify({"error": "Failed to connect to Decent Scale"}), 500
        else:
            return jsonify({"status": "Already connected to Decent Scale"}), 200

@app.route('/enable_notify', methods=['POST'])
def enable_notify():
    with operation_lock:
        if ds.connected:
            ds.enable_notification()
            threading.Thread(target=background_weight_reader, daemon=True).start()
            return jsonify({"status": "Notifications enabled"}), 200
        else:
            return jsonify({"error": "Not connected to Decent Scale"}), 400

@app.route('/disable_notify', methods=['POST'])
def disable_notify():
    with operation_lock:
        if ds.connected:
            ds.disable_notification()
            return jsonify({"status": "Notifications disabled"}), 200
        else:
            return jsonify({"error": "Not connected to Decent Scale"}), 400

@app.route('/weight', methods=['GET'])
def get_weight():
    with weight_lock:
        if latest_weight is not None:
            return jsonify({"weight": latest_weight}), 200
        else:
            return jsonify({"error": "No weight data available"}), 503

@app.route('/tare', methods=['POST'])
def tare():
    with operation_lock:
        if ds.connected:
            ds.tare()
            return jsonify({"status": "Scale tared"}), 200
        else:
            return jsonify({"error": "Not connected to Decent Scale"}), 400

@app.route('/disconnect', methods=['POST'])
def disconnect():
    with operation_lock:
        if ds.connected:
            ds.disable_notification()
            ds.disconnect()
            return jsonify({"status": "Disconnected from Decent Scale"}), 200
        else:
            return jsonify({"error": "Not connected to Decent Scale"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)