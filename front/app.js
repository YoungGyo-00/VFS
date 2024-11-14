const serverUrl = 'ws://127.0.0.1:8080/signaling';
const canvas = document.getElementById('localStreamCanvas');
const context = canvas.getContext('2d');
const videoSettings = { width: 320, height: 240, frameInterval: 30 };

let socket;
let isStreaming = false;
let videoStream = null;
let chunkSize = 8000;

const initializeVideoStream = async () => {
    const video = document.createElement('video');
    video.width = videoSettings.width;
    video.height = videoSettings.height;

    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = videoStream;
        video.play();
        video.addEventListener('play', () => sendFrame(video));
    } catch (error) {
        console.error('Error accessing webcam:', error);
    }
};

const sendFrame = (video) => {
    if (!isStreaming) return;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frame = canvas.toDataURL('image/jpeg', 0.5).split(',')[1];

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
    initializeVideoStream();
};

const handleSocketMessage = (event) => {
    console.log('displayFrame Success');
    displayFrame(`data:image/jpeg;base64,${event.data}`);
};

const handleSocketError = (error) => {
    console.error('WebSocket error:', error);
};

const handleSocketClose = (event) => {
    console.log('WebSocket connection closed', event);
    isStreaming = false;

    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
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