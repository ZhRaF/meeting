// // 007eJxTYFCdupP1+Wb29ZaGYh0fXkTVTf4cUDEleu7pZD/tppNZjT8UGJJTTcyNLS3TUlJNkkzMktISU4ySDQzMTcwNTSwNExMt92zqTmsIZGT4qqDBxMgAgSA+O0NuampJZl46AwMA63whmw==

const APP_ID = 'ce47399fde4b46bfad2c007471491aa9'
const CHANNEL = 'main'
const TOKEN =  '007eJxTYFiaUen+Xa70FINE0jMJ10orfYsCpuZ5q1OWPehbcFnTz0KBITnVxNzY0jItJdUkycQsKS0xxSjZwMDcxNzQxNIwMdHS6kB3WkMgI8OyZwcYGRkgEMRnYchNzMxjYAAA1AIejw=='
let UID;


console.log("streams.js is working");

// Initialize Agora client
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

let localTracks = [];
let remoteUsers = {};

// Function to join and display local stream
let joinAndDisplayLocalStream = async () => {
    try {
 

        // joining the channel

        UID = await client.join(APP_ID, CHANNEL, TOKEN, null);
        console.log('UID:', UID);

        client.on('user-published', handleUserJoined)

        localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
        console.log('Getting the audio and camera of the user');

      // creating an html video element and adding it to the user-${UID} element
        let player = `
            <div class="video-container" id="user-container-${UID}">
                <div class="username-wrapper"><span class="user-name"></span></div>
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
        
        player = `
            <div class="video-container" id="user-container-${user.uid}">
                <div class="username-wrapper"><span class="user-name"></span></div>
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


// Join and display local stream
joinAndDisplayLocalStream();



