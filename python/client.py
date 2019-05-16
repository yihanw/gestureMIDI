from flask import Flask, request
import json
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

obj = {'sensorName': 'gyroscope', 'timestamp': 1555488588153,
       'x': '-0.00466', 'y': '-0.00103', 'z': '0.000938'}


@socketio.on('connect')
def handle_message(message):
    socketio.emit('message', obj)


if __name__ == "__main__":
    socketio.run(app)
