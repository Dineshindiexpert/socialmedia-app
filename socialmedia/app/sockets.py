from flask_socketio import SocketIO, join_room, leave_room, send, emit

socketio = SocketIO()

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    send(f"{data['username']} joined {room}", to=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    send(f"{data['username']} left {room}", to=room)

@socketio.on('message')
def handle_message(data):
    send({'username': data['username'], 'msg': data['msg']}, to=data['room'])

# WebRTC signaling for call
@socketio.on("join-call")
def join_call(data):
    room = data["room"]
    join_room(room)
    emit("new-user", room=room)

@socketio.on("offer")
def handle_offer(data):
    emit("offer", data, broadcast=True)

@socketio.on("answer")
def handle_answer(data):
    emit("answer", data, broadcast=True)

@socketio.on("ice")
def handle_ice(data):
    emit("ice", data, broadcast=True)
