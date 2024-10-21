# Your Theme Song!

A web application that uses your web camera to detect your face and play a theme song of your choosing.

## Motivation

Who doesn't want to have a song that play each time you arrive at work? Professional wrestlers and baseball players have one. Why not you?

## What it does

Your Theme Song! uses facial recognition to detect who you are. If it recognizes you, it will play the theme song you have selected.

If it has never seen you before, it will prompt you to make an account. You'll enter your name, select a song and get your picture taken. The next time the camera sees you, it will play your theme song.

## How to install and run

- Install Python 3
- Create a virtual environment `python -m venv venv`
- Install the dependencies `pip install -r requirements.txt`
- Run the database migrations `reflex db migrate`
- Run the web application `reflex run`