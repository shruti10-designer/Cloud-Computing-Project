var video = document.getElementById('video');
var canvas = document.getElementById('canvas');
var imgDataInput = document.getElementById('img-data');
var captureButton = document.getElementById('capture');
var previewImg = document.getElementById('preview');
var context = canvas.getContext('2d');
var facingMode = 'environment';

function startCamera() {
    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: facingMode
        }
    })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
        captureButton.style.display = 'block';
        canvas.style.display = 'block';
        previewImg.style.display = 'none';

        if (typeof video.setSinkId === 'function') {
            video.setSinkId('default');
        }

        if (facingMode === 'user' || facingMode === 'environment') {
            document.getElementById('switch-camera').style.display = 'block';
        }
    })
    .catch(function(err) {
        console.log(err);
    });
}

function toggleCamera() {
    if (facingMode === 'user') {
        facingMode = 'environment';
    } else {
        facingMode = 'user';
    }

    startCamera();
}

function capture() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    var imgData = canvas.toDataURL('image/jpeg');
    imgDataInput.value = imgData;
    document.getElementById('preview-form').submit();
}