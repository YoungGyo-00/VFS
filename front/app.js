const server_url = 'http://127.0.0.1:8080'
let localStreamElement = document.querySelector('#localStream');
const myKey = Math.random().toString(36).substring(2, 11);
let pcListMap = new Map();
let roomId;
let otherKeyList = [];
let localStream = undefined;

// 웹캠 시작
const startLocalStream = async () =>{
    if(navigator.mediaDevices !== undefined){
        await navigator.mediaDevices.getUserMedia({ audio: true, video : true })
            .then(async (stream) => {
                console.log('Stream found');
                // 웹캠 스트림 정보를 글로벌 변수로 저장한다.
                localStream = stream;
                // Disable the microphone by default
                stream.getAudioTracks()[0].enabled = true;
                localStreamElement.srcObject = localStream;
                // Connect after making sure that local stream is availble

            }).catch(error => {
                console.error("Error accessing media devices:", error);
            });
    }
}

// 소켓 연결
const connectSocket = async () =>{
    const socket = new SockJS(`${server_url}/signaling`);
    stompClient = Stomp.over(socket);
    stompClient.debug = null;

    stompClient.connect({}, () => {
        console.log(`roomId: ${roomId}, camKey: ${myKey}`);
        console.log('Connected to WebRTC server');
        
        // iceCandidate peer 교환을 위한 subscribe
        stompClient.subscribe(`/topic/peer/iceCandidate/${myKey}/${roomId}`, candidate => {
            const key = JSON.parse(candidate.body).key
            const message = JSON.parse(candidate.body).body;
            console.log(`iceCandidate peer 교환 URL : /topic/peer/iceCandidate/${myKey}/${roomId}`)

            // 해당 key에 해당되는 peer 에 받은 정보를 addIceCandidate 해준다.
            pcListMap.get(key).addIceCandidate(new RTCIceCandidate({candidate:message.candidate,sdpMLineIndex:message.sdpMLineIndex,sdpMid:message.sdpMid}));

        });
                
        // offer peer 교환을 위한 subscribe
        stompClient.subscribe(`/topic/peer/offer/${myKey}/${roomId}`, offer => {
            const key = JSON.parse(offer.body).key;
            const message = JSON.parse(offer.body).body;
            console.log(`Offer Peer 교환 URL /topic/peer/offer/${myKey}/${roomId}`)
            // 해당 key에 새로운 peerConnection 를 생성해준후 pcListMap 에 저장해준다.
            pcListMap.set(key,createPeerConnection(key));
            // 생성한 peer 에 offer정보를 setRemoteDescription 해준다.
            pcListMap.get(key).setRemoteDescription(new RTCSessionDescription({type:message.type,sdp:message.sdp}));
            // sendAnswer 함수를 호출해준다.
            sendAnswer(pcListMap.get(key), key);

        });
                
        //answer peer 교환을 위한 subscribe
        stompClient.subscribe(`/topic/peer/answer/${myKey}/${roomId}`, answer =>{
            const key = JSON.parse(answer.body).key;
            const message = JSON.parse(answer.body).body;
                        
            // 해당 key에 해당되는 Peer 에 받은 정보를 setRemoteDescription 해준다.
            pcListMap.get(key).setRemoteDescription(new RTCSessionDescription(message));

        });
                
        //key를 보내라는 신호를 받은 subscribe
        stompClient.subscribe(`/topic/call/key`, message =>{
            //자신의 key를 보내는 send
            stompClient.send(`/app/send/key`, {}, JSON.stringify(myKey));

        });
                
        //상대방의 key를 받는 subscribe
        stompClient.subscribe(`/topic/send/key`, message => {
            const key = JSON.parse(message.body);
            console.log(myKey !== key);
            console.log(otherKeyList.find((mapkey) => mapkey === myKey) === undefined);
                        
            // 만약 중복되는 키가 ohterKeyList에 있는지 확인하고 없다면 추가해준다.
            if(myKey !== key && otherKeyList.find((mapKey) => mapKey === myKey) === undefined){
                otherKeyList.push(key);
                console.log(`otherKeyList : ${otherKeyList}`);
            }
        });

    });
}

const createPeerConnection = (otherKey) =>{
    const pc = new RTCPeerConnection();
    try {
        pc.addEventListener('icecandidate', (event) =>{
            onIceCandidate(event, otherKey);
        });
        pc.addEventListener('track', (event) =>{
            onTrack(event, otherKey);
        });
        if(localStream !== undefined){
            localStream.getTracks().forEach(track => {
                pc.addTrack(track, localStream);
            });
        }

        console.log('PeerConnection created');
    } catch (error) {
        console.error('PeerConnection failed: ', error);
    }
    return pc;
}

const onIceCandidate = (event, otherKey) => {
    if (event.candidate) {
        console.log('ICE candidate');
        stompClient.send(`/app/peer/iceCandidate/${otherKey}/${roomId}`,{}, JSON.stringify({
            key : myKey,
            body : event.candidate
        }));
    }
};

const onTrack = (event, otherKey) => {

    if(document.getElementById(`${otherKey}`) === null){
        const video =  document.createElement('video');

        video.autoplay = true;
        video.controls = true;
        video.id = otherKey;
        video.srcObject = event.streams[0];

        document.getElementById('remoteStreamDiv').appendChild(video);
    }
};

const sendOffer = async (pc ,otherKey) => {
    console.log('Send offer');
    try {
        pc.createOffer().then(offer =>{
            setLocalAndSendMessage(pc, offer);
            stompClient.send(`/app/peer/offer/${otherKey}/${roomId}`, {}, JSON.stringify({
                key : myKey,
                body : offer
            }));
        });
    } catch (error) {
        console.error('Error occured : ', error);
    }
};

const sendAnswer = (pc,otherKey) => {
    pc.createAnswer().then( answer => {
        setLocalAndSendMessage(pc ,answer);
        stompClient.send(`/app/peer/answer/${otherKey}/${roomId}`, {}, JSON.stringify({
            key : myKey,
            body : answer
        }));
        console.log('Send answer');
    });
};

const setLocalAndSendMessage = (pc ,sessionDescription) =>{
    pc.setLocalDescription(sessionDescription);
}

// 룸 번호 입력 후 웹캠 + 웹소켓 실행
document.querySelector('#enterRoomBtn1').addEventListener('click', async () =>{
    await startLocalStream();

    if(localStream !== undefined){
        document.querySelector('#localStream').style.display = 'block';
        document.querySelector('#startSteamBtn').style.display = '';
    }
    roomId = document.querySelector('#roomIdInput').value;
    document.querySelector('#roomIdInput').disabled = true;
    document.querySelector('#enterRoomBtn1').disabled = true;

    await connectSocket();
});

// 스트림 버튼 클릭시 ,다른 웹 key들 웹소켓을 가져 온뒤에 offer -> answer -> iceCandidate 통신
// peer 커넥션은 pcListMap 으로 저장
document.querySelector('#startSteamBtn').addEventListener('click', async () =>{
    await stompClient.send(`/app/call/key`, {}, {});
    console.log('startStreamBtn 누름');
    
    setTimeout(() =>{
        otherKeyList.map((key) =>{
            if(!pcListMap.has(key)){
                console.log('set Key -> sendOffer 실행');
                pcListMap.set(key, createPeerConnection(key));
                sendOffer(pcListMap.get(key),key);
            }
        });
    },1000);
});