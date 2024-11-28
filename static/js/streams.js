const APP_ID = '593278c8e8b048f29c13c30c420f101f';
const CHANNEL = sessionStorage.getItem('hive');
const TOKEN = sessionStorage.getItem('token');
let UID = Number(sessionStorage.getItem('UID'));
const NAME = sessionStorage.getItem('name');

const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
let localTracks = []; // 0 has Audio, 1 has video
let remoteUsers = {};

let socket = new WebSocket(`ws://127.0.0.1:8000/ws/hive/${CHANNEL}/`);

socket.onopen = function () {
    console.log('WebSocket connection established');
};

socket.onerror = function (error) {
    console.error('WebSocket error: ', error);
};

socket.onclose = function () {
    console.log('WebSocket connection closed');
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === 'user-joined') {
        handleUserJoined(data.user, data.mediaType);
    } else if (data.type === 'user-left') {
        handleUserLeft(data.user);
    }
};

// Handle joining stream and displaying local stream
let joinAndDisplayLocalStream = async () => {
    document.getElementById('room-name').innerText = CHANNEL;

    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    try {
        await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {
        console.error(error);
        window.open('/', '_self');
    }

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

    let member = await createMember();

    let player = `<div class="video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`;
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);

    localTracks[1].play(`user-${UID}`);

    await client.publish([localTracks[0], localTracks[1]]);

    // Notify other users that this user has joined
    socket.send(JSON.stringify({
        type: 'user-joined',
        user: { uid: UID, name: member.name },
        mediaType: 'video'
    }));
};

// Handle when another user joins
let handleUserJoined = async (user, mediaType) => {
    try {
        remoteUsers[user.uid] = user;
        await client.subscribe(user, mediaType);

        if (mediaType === 'video') {
            let player = document.getElementById(`user-container-${user.uid}`);
            if (player != null) {
                player.remove();
            }

            let member = await getMember(user);

            player = `<div class="video-container" id="user-container-${user.uid}">
                        <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                        <div class="video-player" id="user-${user.uid}"></div>
                    </div>`;
            document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
            user.videoTrack.play(`user-${user.uid}`);
        }

        if (mediaType === 'audio') {
            user.audioTrack.play();
        }
    } catch (error) {
        console.error('Error handling user join:', error);
    }
};

// Handle when a user leaves the room
let handleUserLeft = (user) => {
    delete remoteUsers[user.uid];
    document.getElementById(`user-container-${user.uid}`).remove();

    // Notify other users that this user has left
    socket.send(JSON.stringify({
        type: 'user-left',
        user: { uid: user.uid }
    }));
};

let leaveAndRemoveLocalStream = async () => {
    for (let i = 0; localTracks.length > i; i++) {
        localTracks[i].stop();
        localTracks[i].close();
    }

    await client.leave();
    deleteMember();

    // Notify others that this user has left
    socket.send(JSON.stringify({
        type: 'user-left',
        user: { uid: UID }
    }));

    window.open('/lobby', '_self');
};

let toggleCamera = async(e)=>{
    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor='#ffff'
    } else{
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor='rgb(255,80,80,1)'
    }
}

let toggleMic = async(e)=>{
    if(localTracks[0].muted){
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor='#ffff'
    } else{
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor='rgb(255,80,80,1)'
    }
}


let createMember = async () => {
    let response = await fetch('/create_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'UID': UID, 'hive_name': CHANNEL })
    });

    let member = await response.json();
    return member;
};

let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&hive_name=${CHANNEL}`);
    let member = await response.json();
    return member;
};

let deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'hive_name': CHANNEL, 'UID': UID })
    });
};

joinAndDisplayLocalStream();

document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream);
document.getElementById('camera-btn').addEventListener('click', toggleCamera);
document.getElementById('mic-btn').addEventListener('click', toggleMic);
window.addEventListener('beforeunload', deleteMember);