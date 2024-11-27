const serverUrl = 'ws://127.0.0.1:8080/signaling';
const canvas = document.getElementById('localStreamCanvas');
const context = canvas.getContext('2d');
const videoSettings = { width: 640, height: 480, frameInterval: 30000 };

let socket;
let isStreaming = false;
let chunkSize = 8000;

const sendFrame = (video) => {
    if (!isStreaming) return;

    const offscreenCanvas = document.createElement('canvas');
    const offscreenContext = offscreenCanvas.getContext('2d');
    offscreenCanvas.width = videoSettings.width;
    offscreenCanvas.height = videoSettings.height;

    offscreenContext.drawImage(video, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
    const frame = offscreenCanvas.toDataURL('image/jpeg', 0.5).split(',')[1];

    const totalChunks = Math.ceil(frame.length / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
        const chunk = frame.slice(i * chunkSize, (i + 1) * chunkSize);
        const message = JSON.stringify({
            chunk,
            chunkIndex: i,
            totalChunks
        });

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(message);
        }
    }

    setTimeout(() => sendFrame(video), videoSettings.frameInterval);
};

const setupWebSocket = () => {
    socket = new WebSocket(serverUrl);

    socket.onopen = handleSocketOpen;
    socket.onmessage = handleSocketMessage;
    socket.onerror = handleSocketError;
    socket.onclose = handleSocketClose;
};

const handleSocketOpen = () => {
    console.log('WebSocket connection established');
    isStreaming = true;

    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            video.addEventListener('play', () => sendFrame(video));
        })
        .catch((error) => {
            console.error('Error accessing webcam:', error);
        });
};

const handleSocketMessage = (event) => {
    console.log('Frame received from server');
    displayFrame(`data:image/jpeg;base64,${event.data}`);
};

const handleSocketError = (error) => {
    console.error('WebSocket error:', error);
};

const handleSocketClose = (event) => {
    console.log('WebSocket connection closed', event);
    isStreaming = false;
};

const displayFrame = (base64Image) => {
    const image = new Image();
    image.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
    };
    image.onerror = (error) => console.error('Error loading image:', error);
    image.src = base64Image;
};

document.getElementById('enterRoomBtn1').addEventListener('click', setupWebSocket);
