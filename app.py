#!/usr/bin/env python

import os
from threading import Lock
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from flask_cors import CORS

import mido
import rtmidi
import uuid

import live

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__, static_url_path='', static_folder='./client/build')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
CORS(app)

thread = None
thread_lock = Lock()

users = {}

class MidiOut():

    def __init__(self, port_name):
        self.port_name = port_name
        # midiout = rtmidi.MidiOut()
        # midiout.open_virtual_port(port_name)
        self.port = mido.open_output(name=port_name, virtual=True)
        print('MIDI port {} opened'.format(self.port_name))

    def close(self):
        print('MIDI port {} closed'.format(self.port_name))
        self.port.close()

class User():

    def __init__(self, sid, name, port_name=None):
        self.sid = sid
        self.uuid = uuid.uuid4()
        self.name = name
        if port_name is None:
            self.port_name = name
        
        self.midi_out = MidiOut(self.port_name)

    def disconnect(self):
        print('User disconnected')
        self.midi_out.close()

def get_user(sid):
    if sid in users.keys():
        return users[sid]
    return None

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')
@app.route('/')
def index():
    root_dir = os.path.dirname(os.getcwd())
    path = os.path.join('client', 'build')
    print(path)
    return send_from_directory(path, 'index.html')
    # return render_template('index.html', async_mode=socketio.async_mode)


class MyNamespace(Namespace):
    def on_midi_event(self, message):
        print("MIDI MESSAGE RECEIVED", message)

        user = get_user(request.sid)
        if user and 'raw' in message.keys():
            midi_data = message['raw']
            msg = mido.Message.from_bytes(midi_data)
            print(user.name, 'sent:', midi_data, type(midi_data), msg)
            # msg.copy(channel=1)
            user.midi_out.port.send(msg)

        # session['receive_count'] = session.get('receive_count', 0) + 1
        # emit('my_response', {'data': message['data'], 'count': session['receive_count']})

    def on_my_broadcast_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             broadcast=True)

    def on_join(self, message):
        join_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_leave(self, message):
        leave_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_close_room(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                             'count': session['receive_count']},
             room=message['room'])
        close_room(message['room'])

    def on_my_room_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             room=message['room'])

    def on_disconnect_request(self):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_my_ping(self):
        emit('my_pong')

    def on_connect(self):
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread)

    def on_disconnect(self):
        print('Client disconnected', request.sid)
        if request.sid in users:
            user = users[request.sid]
            user.disconnect()
            del users[request.sid]

    def on_join_midi(self, data):
        user_name = data['username']
        sid = request.sid

        user = User(sid, user_name)
        users[sid] = user

        userDict = {
            'uuid': str(user.uuid),
            'userName': user.name,
            'sid': user.sid
        }
        emit('on_connect', {'msg': 'Connected', 'user': userDict, 'tracks': [str(track) for track in set.tracks]})
        emit('user_joined', { 'user': userDict })


socketio.on_namespace(MyNamespace('/test'))

if __name__ == '__main__':
    set = live.Set(address=("localhost", 9000))
    set.scan(scan_clip_names = True, scan_devices = True)
    track = set.tracks[0]
    print("Track name %s" % track.name)
    socketio.run(app, host='0.0.0.0', port=80, debug=False) #os.environ.get('PORT', 80), debug=True) # debug=True)
