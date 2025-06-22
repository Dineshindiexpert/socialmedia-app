const socket = io();
let localStream, peerConnection;
const config = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");

function joinCall() {
    const room = document.getElementById("room").value.trim();
    socket.emit("join-call", { room });

    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            localStream = stream;
            localVideo.srcObject = stream;
        });
}

socket.on("new-user", () => {
    createPeer(true);
});

socket.on("offer", data => {
    createPeer(false);
    peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
    peerConnection.createAnswer().then(answer => {
        peerConnection.setLocalDescription(answer);
        socket.emit("answer", { answer });
    });
});

socket.on("answer", data => {
    peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
});

socket.on("ice", data => {
    if (peerConnection) {
        peerConnection.addIceCandidate(new RTCIceCandidate(data.ice));
    }
});

function createPeer(initiator) {
    peerConnection = new RTCPeerConnection(config);

    peerConnection.onicecandidate = event => {
        if (event.candidate) {
            socket.emit("ice", { ice: event.candidate });
        }
    };

    peerConnection.ontrack = event => {
        remoteVideo.srcObject = event.streams[0];
    };

    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });

    if (initiator) {
        peerConnection.createOffer().then(offer => {
            peerConnection.setLocalDescription(offer);
            socket.emit("offer", { offer });
        });
    }
}
