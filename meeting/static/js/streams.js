// // 007eJxTYFCdupP1+Wb29ZaGYh0fXkTVTf4cUDEleu7pZD/tppNZjT8UGJJTTcyNLS3TUlJNkkzMktISU4ySDQzMTcwNTSwNExMt92zqTmsIZGT4qqDBxMgAgSA+O0NuampJZl46AwMA63whmw==

const APP_ID = 'ce47399fde4b46bfad2c007471491aa9'
const CHANNEL = sessionStorage.getItem('room')
const TOKEN =  sessionStorage.getItem('token')
let UID =  Number(sessionStorage.getItem('UID'))

let USERNAME=sessionStorage.getItem('username')
// '007eJxTYFiaUen+Xa70FINE0jMJ10orfYsCpuZ5q1OWPehbcFnTz0KBITnVxNzY0jItJdUkycQsKS0xxSjZwMDcxNzQxNIwMdHS6kB3WkMgI8OyZwcYGRkgEMRnYchNzMxjYAAA1AIejw=='


console.log("streams.js is working");

// Initializing Agora client
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

let localTracks = [];
let remoteUsers = {};

// Function to join and display local stream
let joinAndDisplayLocalStream = async () => {
    try {
        // joining the channel

        await client.join(APP_ID, CHANNEL, TOKEN, UID);
        console.log('UID:', UID);

        document.getElementById('room-name').textContent = CHANNEL

        client.on('user-published', handleUserJoined)
        client.on('user-left', handleUserLeft)


        localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
        console.log('Getting the audio and camera of the user');
       
        let member = await createMember()
      // creating an html video element and adding it to the user-${UID} element
        let player = `
            <div class="video-container" id="user-container-${UID}">
                <div class="username-wrapper"><span class="user-name">${member.username}</span></div>
                <div class="video-player" id="user-${UID}"></div>
            </div>
        `;
        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        localTracks[1].play(`user-${UID}`);

      // other users get access to the client tracks
        await client.publish([localTracks[0], localTracks[1]]);
    } catch (error) {
        console.error('Error joining and displaying local stream:', error);
        // Optionally redirect or handle the error
        // window.open('/', '_self');
    }
};



// ----------------------------------------------------------
let handleUserJoined = async (user,mediaType) => {
    remoteUsers[user.uid] = user;
    await client.subscribe(user, mediaType);

    if (mediaType === 'video') {
        let player = document.getElementById(`user-container-${user.uid}`);
        
        // If the user had to refresh or lost connection, we need to refresh it
        if (player != null) {
            // player.parentNode.remove()
            // test
            player.remove();
            
        }

        let member= await getMember(user)
        
        player = `
            <div class="video-container" id="user-container-${user.uid}">
                <div class="username-wrapper"><span class="user-name">${member.username}</span></div>
                <div class="video-player" id="user-${user.uid}"></div>
            </div>
        `;
        
        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        
        // Ensure the video element is in the DOM
        let videoElement = document.getElementById(`user-${user.uid}`);
        if (videoElement) {
            user.videoTrack.play(`user-${user.uid}`);
        } else {
            console.error('Video element not found:', `user-${user.uid}`);
        }
    }

    if (mediaType === 'audio') {
        user.audioTrack.play();
    }

}

let handleUserLeft = async(user) => {
    delete remoteUsers[user.uid]
    document.getElementById(`user-container-${user.uid}`).remove()

}

let leaveAndRemoveLocalStream = async () => {
    for (let track of localTracks) {
        track.stop();
        track.close();
    }

    await client.leave();

    deleteMember()
    window.open('/lobby', '_self');
};

let toggleCamera = async (e) =>{
    
    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        e.target.textContent = 'turn camera off'

    }
   else{
        await localTracks[1].setMuted(true)
        e.target.textContent = 'turn camera on'

    }
}
let toggleAudio = async (e) => {
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false);
        e.target.textContent = 'Mute';
    } else {
        await localTracks[0].setMuted(true);
        e.target.textContent = 'Unmute';
    }
};

let createMember = async () => {
    let response = await fetch('createMember/', {
        method:'POST',
        headers: {
            'Content-Type':'application/json'
        },
        body:JSON.stringify({'username':USERNAME, 'room_name':CHANNEL, 'UID':UID})
    })
    let member = await response.json()
    return member
}

let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`)
    let member = await response.json()
    return member
}

let deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method:'POST',
        headers: {
            'Content-Type':'application/json'
        },
        body:JSON.stringify({'username':USERNAME, 'room_name':CHANNEL, 'UID':UID})
    })
    let member = await response.json()
}


let camera= document.querySelector('#button-camera').addEventListener('click',toggleCamera)
let audio= document.querySelector('#button-audio').addEventListener('click',toggleAudio)
let leave= document.querySelector('#button-leave').addEventListener('click',leaveAndRemoveLocalStream)


// Join and display local stream
joinAndDisplayLocalStream();

window.addEventListener('beforeunload',deleteMember)


