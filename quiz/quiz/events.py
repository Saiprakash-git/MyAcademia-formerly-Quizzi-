from quiz import socketio
from flask_login import current_user
from flask import request


@socketio.on('connect')
def handle_connect():
    
    socketio.emit('user', {"username": current_user.username})

