const player = document.getElementById('player');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const getStartedButton = document.getElementById('getStarted');

const constraints = {
  video: true,
};

let pictures = [];

let data = new FormData();

function createImage() {
  context.drawImage(player, 0, 0, canvas.width, canvas.height);
  // pictures.unshift(canvas.toDataURL());
  // var imageData = context.getImageData(0,0, canvas.width, canvas.height)
  // context.putImageData(player, 0, 0)
  const dataURL = canvas.toDataURL();
  // console.log(imageData)
  console.log('making call')
  // const headers = {'Content-Type': imageData.type}
  axios.post('http://127.0.0.1:5000/check', {image: dataURL})
    .then(function (response) {
      console.log(response);
      console.log('play a song at this point')
    })
    .catch(function (error) {
      console.log(error);
    });
}

getStartedButton.addEventListener('click', () => {
  player.removeAttribute("class");
  // Attach the video stream to the video element and autoplay.
  navigator.mediaDevices.getUserMedia(constraints)
    .then((stream) => {
      player.srcObject = stream;
    });
  getStartedButton.className = "hidden";
  setInterval(function() {
    createImage();
  }, 2000);
})