const afterPhotoDiv = document.getElementById('after-photo')
const anotherPictureButton = document.getElementById('another-picture')
const canvas = document.getElementById('canvas')
const context = canvas.getContext('2d')
const getStartedButton = document.getElementById('get-started')
const keepPictureButton = document.getElementById('keep-picture')
const player = document.getElementById('player')
const saveButton = document.getElementById('save-button')
const searchButton = document.getElementById('search-button')
const searchField = document.getElementById('search-field')
const selectedSongOutput = document.getElementById('selected-song-output')
const songResults = document.getElementById('song-results')
const takePictureButton = document.getElementById('take-picture')
let possibleSongs = []
let selectedSong = null
let savedImage = null
let containsErrors = true

anotherPictureButton.addEventListener('click', () => {
  canvas.classList.add('hidden')
  afterPhotoDiv.classList.add('hidden')
  player.classList.remove('hidden')
  takePictureButton.classList.remove('hidden')
})

getStartedButton.addEventListener('click', () => {
  player.removeAttribute("class")
  canvas.classList.remove('hidden')
  canvas.classList.add('hidden')
  navigator.mediaDevices.getUserMedia({video: true})
    .then((stream) => {
      player.srcObject = stream
    })
  getStartedButton.classList.add('hidden')
  takePictureButton.classList.remove('hidden')
})

keepPictureButton.addEventListener('click', () => {
  player.classList.add('hidden')
  getStartedButton.classList.remove('hidden')
  afterPhotoDiv.classList.add('hidden')
})

takePictureButton.addEventListener('click', () => {
  context.drawImage(player, 0, 0, canvas.width, canvas.height)
  savedImage = canvas.toDataURL('image/png')
  player.classList.add('hidden')
  canvas.classList.remove('hidden')
  takePictureButton.classList.add('hidden')
  afterPhotoDiv.classList.remove('hidden')
})

function performSearch(searchTerm) {
  axios.get('/search/' + searchTerm)
    .then(function (response) {
      songResults.innerHTML = ''
      const template = document.getElementById('t-song-result')
      possibleSongs = []
      response.data.songs.forEach(songResult => {
        possibleSongs.push(songResult)
        var clone = document.importNode(template.content, true)
        let title = songResult.title;
        const cartTitle = clone.querySelector('.card-title')
        if (title.length > 28) {
          title = title.substring(0, 28);
        }
        if (songResult.explicit) {
          title += " | <span class='text-danger'><strong>EXPLICIT</strong></span>"
        }
        cartTitle.appendChild(document.createTextNode(title));
        clone.querySelector('.card-title').innerHTML = title
        const subtitle = clone.querySelector('.card-subtitle')
        if (songResult.image_url) {
          const thumbnail = document.createElement('img')
          thumbnail.setAttribute("src", songResult.image_url);
          subtitle.appendChild(thumbnail)
        }
        subtitle.appendChild(document.createTextNode(" By " + songResult.artist))
        const cardText = clone.querySelector('.card-text')
        const sourceTag = document.createElement('source')
        sourceTag.setAttribute('src', songResult.url)
        const audioTag = document.createElement('audio')
        audioTag.setAttribute('controls', null)
        audioTag.appendChild(sourceTag)
        cardText.appendChild(audioTag)
        const cartSelectButton = clone.querySelector('.card-select-button')
        cartSelectButton.addEventListener('click', event => {
          const clickedCard = event.target.parentNode.parentNode
          let index = -1;
          let i = 0
          for (const card of document.querySelectorAll('.card')) {
            card.classList.remove("selected-card")
            if (card === clickedCard) {
              index = i
            }
            i++
          }
          clickedCard.classList.add('selected-card')
          selectedSong = possibleSongs[index]
          selectedSongOutput.innerHTML = selectedSong.title
        })
        songResults.appendChild(clone)
      });
    })
    .catch(function (error) {
      console.log(error)
    });
}

function checkError(field) {
  const tag = document.getElementById(field)
  const value = tag.value
  if (!value) {
    tag.classList.add('error-field')
    const titleCaseField = field.charAt(0).toUpperCase() + field.slice(1)
    document.getElementById(field + '-error').innerHTML = titleCaseField + ' required'
    containsErrors = true
  }
}

function clearErrors() {
  containsErrors = false
  const tagIds = ['name', 'email', 'password']
  for (const tagId of tagIds) {
    document.getElementById(tagId).classList.remove('error-field')
    const errorTag = document.getElementById(tagId + '-error')
    errorTag.innerHTML = ''
  }
  document.getElementById('photo-error').innerHTML = ''
  searchField.classList.remove('error-field')
  document.getElementById('song-error').innerHTML = ''
}

saveButton.addEventListener('click', () => {
  clearErrors()
  checkError('name')
  checkError('email')
  checkError('password')
  if (!selectedSong) {
    document.getElementById('song-error').innerHTML = 'Song required'
    searchField.classList.add('error-field')
    containsErrors = true
  }
  if (!savedImage) {
    document.getElementById('photo-error').innerHTML = 'Photo required'
    containsErrors = true;
  }
  if (!containsErrors) {
    const name = document.getElementById('name').value
    const email = document.getElementById('email').value
    const password = document.getElementById('password').value
    axios.post('/user', {
        image: savedImage,
        name: name,
        email: email,
        password: password,
        song: selectedSong
      })
      .then(function (response) {
        window.location = "/success"
      })
      .catch(function (error) {
        console.log(error)
      });
  }
})

searchButton.addEventListener('click', () => {
  performSearch(searchField.value)
})

searchField.addEventListener('keyup', (event) => {
  if (event.keyCode === 13) {
    performSearch(searchField.value)
  }
})