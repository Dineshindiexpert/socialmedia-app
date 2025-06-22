const socket = io();
let currentRoom = '';

function joinRoom() {
    const room = document.getElementById("room").value.trim();
    if (!room) return;

    if (currentRoom) {
        socket.emit('leave', { room: currentRoom, username });
    }

    currentRoom = room;
    socket.emit('join', { room, username });

    const box = document.getElementById("chatBox");
    box.innerHTML += `<div><em>Joined room: ${room}</em></div>`;
}

function sendMsg() {
    const msg = document.getElementById("msgInput").value.trim();
    if (msg && currentRoom) {
        socket.emit('message', { room: currentRoom, username, msg });
        document.getElementById("msgInput").value = "";
    }
}

socket.on('message', data => {
    const box = document.getElementById("chatBox");
    if (typeof data === "string") {
        box.innerHTML += `<div><em>${data}</em></div>`;
    } else {
        box.innerHTML += `<div><strong>${data.username}:</strong> ${data.msg}</div>`;
    }
    box.scrollTop = box.scrollHeight;
});
