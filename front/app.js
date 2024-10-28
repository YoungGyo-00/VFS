const serverUrl = 'ws://127.0.0.1:8080/signaling';
const canvas = document.getElementById('localStreamCanvas');
const context = canvas.getContext('2d');

const connectSocket = () => {
    const socket = new WebSocket(serverUrl);

    socket.onopen = () => {
        console.log('WebSocket connection established');
    };

    socket.onmessage = (event) => {
        const base64Image = event.data;
        console.log('Received Base64 Image Data:', base64Image);
        displayFrame(base64Image);
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
    };
};

const displayFrame = (base64Image) => {
    const image = new Image();
    image.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
    };
    image.onerror = (error) => {
        console.error('Error loading image:', error);
    };
    image.src = base64Image;
};

document.getElementById('enterRoomBtn1').addEventListener('click', () => {
    connectSocket();
});