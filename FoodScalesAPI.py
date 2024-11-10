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

# Global variables to hold the DecentScale object and the latest weight value
ds = DecentScale()
weight_lock = threading.Lock()
operation_lock = threading.Lock()  # New lock to prevent concurrent operations
latest_weight = None

def connect_and_read_weight():
    global latest_weight

    with operation_lock:  # Ensure only one operation happens at a time
        if not ds.connected:
            connected = ds.auto_connect()
        else:
            connected = True

        if connected:
            print("Connected to Decent Scale")
            ds.enable_notification()
            asyncio.run(read_weight())
            ds.disable_notification()
            ds.disconnect()
            print("Disconnected from Decent Scale")
        else:
            print("Failed to connect to Decent Scale")

async def read_weight():
    global latest_weight
    print('Reading values...')
    for _ in range(50):
        with weight_lock:
            if ds.weight is not None:
                latest_weight = ds.weight
                print(f'Current weight: {ds.weight:.1f} g', end='\r')
        await asyncio.sleep(0.1)
    print('\nFinished reading values.')

@app.route('/weight', methods=['GET'])
def get_weight():
    global latest_weight
    with weight_lock:
        if latest_weight is not None:
            print(f"Returning weight: {latest_weight:.1f} g")
            return jsonify({"weight": latest_weight})
        else:
            print("No weight data available")
            return jsonify({"error": "No weight data available"}), 503

@app.route('/start', methods=['POST'])
def start_reading():
    threading.Thread(target=connect_and_read_weight).start()
    return jsonify({"status": "Weight reading started"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)