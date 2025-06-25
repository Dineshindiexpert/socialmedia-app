from flask_socketio import emit, join_room
from app import socketio, db
from app.models import Message, User
from flask import request

@socketio.on('connect')
def handle_connect():
    print("User connected:", request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message_text = data['message']

    # Save to database
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, message=message_text)
    db.session.add(msg)
    db.session.commit()

    sender = User.query.get(sender_id)

    # Emit to both sender and receiver
    emit('receive_message', {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': message_text,
        'sender_name': sender.username
    }, broadcast=True)
@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data['to'])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data['to'])

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    emit('ice-candidate', data, room=data['to'])
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"User joined room: {room}")
