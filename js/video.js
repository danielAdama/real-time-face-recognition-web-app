
// Means open the user's webcam without permission and ignore the
// audio
const mediaStreamConstraints = {
    audio: false,
    video: true
}

let captureFrame = null;
let controller, videoElem, tmpCanvas, tmpContext;

tmpCanvas = document.createElement('canvas');
document.getElementById("open-btn").addEventListener("click", (e) => {
    e.preventDefault();
    accessCamera();
});
document.getElementById("close-btn").addEventListener("click", (e) => {
    e.preventDefault();
    closeCamera();
});

const name_var = document.getElementById("name-var");
document.getElementById("train-btn").addEventListener("click", async function(){
    videoElem = document.getElementById("video");
    checkName = name_var.value.toLowerCase().replace(" ", "_");
    const errorElem = document.getElementById('error');
    try
    {
        const name = checkName.toLowerCase().replace(" ", "_");
        await screenshot(name);
        
    }
    catch(err)
    {
        errorElem.innerHTML = err;
        errorElem.style.display = "block";
        console.log(err);
    }
});

async function screenshot(name){
    try
    {
        let imgCanvas = document.createElement('canvas');
        let computedStyle = window.getComputedStyle(videoElem);
        let bgr = computedStyle.getPropertyValue('background-color');
        imgCanvas.setAttribute("width",parseInt(video.offsetWidth));
        imgCanvas.setAttribute("height",parseInt(video.offsetHeight));
        let imgContext = imgCanvas.getContext("2d");
        imgContext.drawImage(videoElem, 0, 0, imgCanvas.width, imgCanvas.height);
        const imageUrl = await imgCanvas.toDataURL("image/jpeg");
        /* Convert the imageUrl from base64 to bolb and then json for faster processing */
        const data = imageUrl.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
        const resp = await fetch(
            "http://127.0.0.1:8080/api/v1/train",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    'name':name,
                    'image':data
                })
            }
        );
        const jsn = await resp.json();
        console.log(jsn);
    }
    catch(err)
    {
        errorElem.innerHTML = err;
        errorElem.style.display = "block";
        console.log(err);
    }
}

async function accessCamera(){
    videoElem = document.getElementById("video");
    const errorElem = document.getElementById('error');
    let stream = null;
    try
    {
        stream = await window.navigator.mediaDevices.getUserMedia(mediaStreamConstraints);
        /* The received mediaStream contains both the video and audio media data*/
        // Adding the received stream to the source of the video element
        videoElem.srcObject = stream;
        videoElem.autoplay = true;
        captureFrame = stream;
        await init();
    }
    catch(err)
    {
        errorElem.innerHTML = err;
        errorElem.style.display = "block";
        console.log(err);
    }
    
}
async function closeCamera(){
    videoElem = document.getElementById("video");
    const errorElem = document.getElementById('error');
    /* MediaStream.getTracks() returns an array of all the 
    MediaStreamTracks being used in the received mediaStream
    we can iterate through all the mediaTracks and 
    stop all the mediaTracks by calling its stop() method*/
    try
    {
        captureFrame.getTracks().forEach(mediaTrack => {
        mediaTrack.stop();
        });
        let computedStyle = window.getComputedStyle(videoElem);
        let bgr = computedStyle.getPropertyValue('background-color');
        if (bgr === "rgb(0, 0, 0)" || bgr === "#000000"){
            controller.abort();
            var timeoutId = await computeFrame();
            clearTimeout(timeoutId);
            console.log(`Timeout ID ${timeoutId} has been cleared`);
            console.log("Frame rendering aborted");
        }
    }
    catch(err)
    {
        errorElem.innerHTML = "Camera closed successfully";
        errorElem.style.display = "block";
        console.log(err);
    }
}

async function init(){
    videoElem = await document.getElementById("video");
    tmpCanvas.setAttribute("width",parseInt(videoElem.offsetWidth));
    tmpCanvas.setAttribute("height",parseInt(videoElem.offsetHeight));
    tmpContext = await tmpCanvas.getContext("2d");
    videoElem.addEventListener("play", computeFrame);
}

async function computeFrame(){
    controller = new AbortController();
    const signal = controller.signal;
    /* Get current video frame as image */
    try
    {
        tmpContext.drawImage(videoElem, 0, 0, videoElem.width, videoElem.height);
        const imageUrl = await tmpCanvas.toDataURL("image/jpeg");
        /* Convert the imageUrl from base64 to bolb and then json for faster processing */
        const data = imageUrl.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
        //const bolb = new Blob([imageUrl], {type:"image/jpeg"});
        const resp = await fetch(
            "http://127.0.0.1:8080/api/v1/verify",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data),
                signal: signal
            }
        );
        const jsn = await resp.json();
        if (jsn.BaseResponse.Status === true){
            console.log(jsn);
        }

        var timeId = setTimeout(computeFrame, 0);
    }
    catch(err)
    {
        console.log(err);
    }
    return timeId;
};
