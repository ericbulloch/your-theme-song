import base64
import json
import os
import sqlite3

import deezer
from flask import Flask, jsonify, render_template, request, send_from_directory

import cv2
import face_recognition
from flask import Flask, request
from flask_cors import CORS
import numpy

# the following might now be needed
import base64
import re
import io
from PIL import Image


APP = Flask(__name__)


DATABASE = 'database.db'


def ensure_database():
    if os.path.exists(DATABASE):
        return
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE users
                 (id integer PRIMARY KEY AUTOINCREMENT, name text, email text, password text, hash text, song_id integer)''')
    cursor.execute('''CREATE TABLE songs
                 (id integer PRIMARY KEY AUTOINCREMENT, title text, artist text, url text)''')
    connection.commit()
    connection.close()


def save_song(title, artist, url):
    song_id = None
    ensure_database()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO songs (title, artist, url) VALUES ('{title}', '{artist}', '{url}')")
    connection.commit()
    song_id = cursor.lastrowid
    connection.close()
    return song_id


def save_user(name, email, password, song_id):
    user_id = None
    ensure_database()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO users (name, email, password, song_id) VALUES ('{name}', '{email}', '{password}', {song_id})")
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return user_id


def get_users():
    users = []
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''SELECT
            u.name as name, s.title as title, s.artist as artist, s.url as url 
        FROM 
            users u
        INNER JOIN songs s 
            ON u.song_id = s.id''')
    users = [row for row in cursor.fetchall()]
    connection.close()
    return users


def convert_and_save(b64_image_string, filename):
    with open(f'static/images/{filename}.png', 'wb') as fh:
        fh.write(base64.b64decode(b64_image_string))


def create_deezer_result(search_result):
    result = {
        'title': search_result.title,
        'artist': search_result.artist.name,
        'url': search_result.preview,
        'explicit': search_result.explicit_lyrics,
        'image_url': search_result.artist.picture_small
    }
    return result


@APP.route('/')
def index():
    return render_template('index.html')


@APP.route('/client')
def client():
    return render_template('client.html')


@APP.route('/success')
def success():
    return render_template('success.html')


@APP.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@APP.route('/search/<term>', methods=['GET'])
def search(term):
    term = term.strip()
    error = ''
    songs = []
    if not term:
        error = 'Please search for an artist or song title'
    else:
        client = deezer.Client(headers={'Accept-Language': 'en'})
        songs_results = client.search(term, limit=20)
        for r in songs_results:
            songs.append(create_deezer_result(r))
    return jsonify({'error': error, 'songs': songs})


@APP.route('/user', methods=['POST'])
def user_post():
    data = request.get_json()
    image_name = '_'.join(data['name'].split(' ')).lower()
    convert_and_save(data['image'].split(',')[1], image_name)
    song_id = save_song(data['song']['title'], data['song']['artist'], data['song']['url'])
    user_id = save_user(data['name'], data['email'], data['password'], song_id)
    return jsonify({'error': '', 'user_id': user_id})


@APP.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    image_array = data
    ensure_database()
    arr = numpy.array(image_array, dtype=numpy.uint8)
    face_locations = face_recognition.face_locations(arr)
    face_encodings = face_recognition.face_encodings(arr, face_locations)
    users = get_users()
    known = []
    for user in users:
        filename = '_'.join(user[0].split(' ')).lower()
        image = face_recognition.load_image_file(f'static/images/{filename}.png')
        encoding = face_recognition.face_encodings(image)[0]
        known.append({
            'name': user[0],
            'display': user[0].split(' ')[0],
            'encoding': encoding,
            'url': user[3]
        })

    known_face_encodings = [k['encoding'] for k in known]
    known_face_names = [k['name'] for k in known]
    known_face_display = [k['display'] for k in known]
    urls = [k['url'] for k in known]
    name = 'Unknown'
    results = []
    for i, face_encoding in enumerate(face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = numpy.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            results.append({
                'display': known_face_display[best_match_index],
                'name': known_face_names,
                'score': face_distances[best_match_index],
                'position': face_locations[i],
                'url': urls[best_match_index],
            })
    return json.dumps(results)


if __name__ == '__main__':
    extra_dirs = ['static', 'templates']
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    # APP.run(host='0.0.0.0', port=8000, debug=True, extra_files=extra_files)
    APP.run(host='0.0.0.0')