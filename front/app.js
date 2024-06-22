const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');

const socket = new SockJS('/api/fit');
const stompClient = Stomp.over(socket);

let localStream;
let pc;  // RTCPeerConnection 객체

stompClient.connect({}, (frame) => {
    console.log('Connected: ' + frame);
    stompClient.subscribe('/topic/messages', async (messageOutput) => {
        const message = JSON.parse(messageOutput.body);

        switch (message.type) {
            case 'join':
                console.log('Joined room');
                await startLocalStream();
                await createPeerConnection();
                break;
            case 'offer':
                console.log('Received offer');
                await pc.setRemoteDescription(new RTCSessionDescription(message.sdp));
                const answer = await pc.createAnswer();
                await pc.setLocalDescription(answer);
                sendMessage({
                    type: 'answer',
                    sdp: answer
                });
                break;
            case 'answer':
                console.log('Received answer');
                await pc.setRemoteDescription(new RTCSessionDescription(message.sdp));
                break;
            case 'candidate':
                console.log('Received ICE candidate');
                await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    });

    sendMessage({ type: 'join' });
});

async function startLocalStream() {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
}

async function createPeerConnection() {
    pc = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    });

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            sendMessage({
                type: 'candidate',
                candidate: event.candidate
            });
        }
    };

    pc.ontrack = (event) => {
        if (remoteVideo.srcObject !== event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
        }
    };

    localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    sendMessage({
        type: 'offer',
        sdp: offer
    });
}

function sendMessage(message) {
    stompClient.send("/app/message", {}, JSON.stringify(message));
}
