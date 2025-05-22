# Your Theme Song!

A web application that uses your web camera to detect your face and play your theme song!

## Motivation

Who doesn't want to have a theme song that play each time you arrive at work?

- Professional wrestlers pump up the crowd as they are walking to the ring.
- Baseball players have a walk up song when they head to the plate.
- Starters for basketball teams have music playing while they get announced.

**Why not you?**

## What it does

Your Theme Song! uses facial recognition to detect who you are. If it recognizes you, it will play your theme song!

If it has never seen you before, it will prompt you to make an account. You'll enter your name, select a song and get your picture taken. The next time the camera sees you, it will play your theme song.

Families and friends love this project! People smile big when their theme song starts playing after their face has been recognized.

## How to install and run

- Install Python 3
- Create a virtual environment `python -m venv venv`
- Install the dependencies `pip install -r requirements.txt`
- Run the database migrations `reflex db migrate`
- Run the web application `reflex run`
