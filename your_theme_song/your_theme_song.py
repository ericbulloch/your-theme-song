"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import glob
import time
from typing import List
from urllib.request import urlopen

import deezer
import face_recognition
from PIL import Image
import reflex as rx
import reflex_webcam


class User(rx.Model, table=True):
    name: str
    song_title: str
    song_url: str
    screenshot_url: str


class UserState(rx.State):
    name: str = ""
    song_artist: str = ""
    song_title: str = ""
    song_url: str = ""
    search: str = ""
    state: str = "form"
    loading: bool = False
    last_screenshot: Image.Image | None = None
    screenshot: Image.Image | None = None
    search_results: List[dict[str, str]] = []
    error_message: str = ""

    def handle_submit(self):
        print('Clicked submit')
        print(self.last_screenshot)
        print(self.name)
        print(self.song_artist)
        print(self.song_title)
        print(self.song_url)
    
    def handle_open_picture_form(self):
        self.state = 'picture'
    
    def handle_open_song_form(self):
        self.state = 'song'

    def handle_take_picture(self, img_data_uri: str):
        if self.loading:
            return
        with urlopen(img_data_uri) as img:
            image = face_recognition.load_image_file(img)
            face_locations = face_recognition.face_locations(image)
            self.error_message = ""
            if face_locations:
                unknown_encoding = face_recognition.face_encodings(image)[0]
                found = False
                for known_image_path in glob.glob('images/*.jpg'):
                    known_image = face_recognition.load_image_file(known_image_path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
                    if results[0]:
                        self.error_message = "You already have an account"
                        found = True
                        break
                if not found:
                    self.last_screenshot = Image.open(img)
                    self.last_screenshot.load()
                    self.last_screenshot.format = "WEBP"
    
    def handle_accept_image(self):
        if not self.last_screenshot:
            self.error_message = "Please take a screenshot"
            return
        self.screenshot = self.last_screenshot
        self.state = 'form'
    
    def handle_search(self):
        if not self.search:
            return
        with deezer.Client() as client:
            self.search_results = []
            results = client.search(self.search)
            print('results', results)
            for result in results:
                self.search_results.append(dict(title=result.title, url=result.preview, artist=result.artist.name))
    
    def handle_select_song(self, song: dict[str, str]):
        self.search = ''
        self.song_artist = song['artist']
        self.song_title = song['title']
        self.song_url = song['url']
        self.search_results = []
        self.state = 'form'
    
    def handle_cancel(self):
        self.state = 'form'


class State(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    loading: bool = False
    user: dict | None = None
    create_profile: bool = False

    def handle_screenshot(self, img_data_uri: str):
        print('handle_screenshot', img_data_uri)
        if self.loading:
            return
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")
        self.create_profile = False
        with urlopen(img_data_uri) as img:
            self.last_screenshot = Image.open(img)
            self.last_screenshot.load()
            self.last_screenshot.format = "WEBP"
            self.user = None
            image = face_recognition.load_image_file(img)
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                unknown_encoding = face_recognition.face_encodings(image)[0]
                found = False
                for known_image_path in glob.glob('images/*.jpg'):
                    known_image = face_recognition.load_image_file(known_image_path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
                    if results[0]:
                        self.user = dict(name="Person", song_title="Some Song")
                        found = True
                        break
                if not found:
                    self.create_profile = True


def last_screenshot_widget(last_screenshot: Image.Image | None) -> rx.Component:
    return rx.box(
        rx.cond(
            last_screenshot,
            rx.fragment(
                rx.image(src=last_screenshot),
            ),
            rx.center(
                rx.text("Click image to capture.", size="4"),
            ),
        ),
        height="45vh",
    )


def webcam_upload_component(ref: str, handler) -> rx.Component:
    return rx.vstack(
        reflex_webcam.webcam(
            id=ref,
            on_click=reflex_webcam.upload_screenshot(
                ref=ref,
                handler=handler,
            ),
        ),
        width="45vh",
        align="center",
    )


def render_search_result(item: dict[str, str]):
    return rx.hstack(
        rx.button(
            "Select song",
            on_click=lambda: UserState.handle_select_song(item),
            background_color="green",
        ),
        rx.text(item.artist),
        rx.text(item.title),
        rx.audio(
            url=item.url,
            width="150px",
            height="32px",
        ),
    )


def render_search_results(search_results: List[dict]) -> rx.Component:
    return rx.vstack(
        rx.text('Search Results'),
        rx.vstack(
            rx.foreach(
                search_results, render_search_result
            )
        )
    )


def render_error_message(text: str) -> rx.Component:
    return rx.text(
        text,
        size="7",
        weight="bold",
        color_scheme="red"
    )


def create() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.cond(
            UserState.state == 'form',
            rx.vstack(
                rx.heading("Create Your Theme Song!", size="9"),
                rx.cond(
                    UserState.error_message,
                    render_error_message(UserState.error_message),
                ),
                rx.input(
                    placeholder="What is your name?",
                    value=UserState.name,
                    on_change=UserState.set_name,
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            UserState.screenshot,
                            "Update picture",
                            "Take a picture",
                        ),
                        on_click=UserState.handle_open_picture_form,
                    ),
                    rx.cond(
                        UserState.screenshot,
                        rx.text("✓"),
                    ),
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            UserState.song_title,
                            "Update song",
                            "Pick a song",
                        ),
                        on_click=UserState.handle_open_song_form,
                    ),
                    rx.cond(
                        UserState.song_title,
                        rx.text(UserState.song_title),
                    ),
                ),
                rx.button(
                    "Submit",
                    on_click=UserState.handle_submit,
                ),
            ),
        ),
        rx.cond(
            UserState.state == 'picture',
            rx.vstack(
                rx.heading("Take a picture!", size="9"),
                rx.cond(
                    UserState.error_message,
                    render_error_message(UserState.error_message),
                ),
                rx.hstack(
                    webcam_upload_component("picture", UserState.handle_take_picture),
                    last_screenshot_widget(UserState.last_screenshot),
                ),
                rx.hstack(
                    rx.button(
                        "Cancel",
                        on_click=UserState.handle_cancel,
                    ),
                    rx.button(
                        "Accept",
                        disable=UserState.last_screenshot,
                        on_click=UserState.handle_accept_image,
                    )
                ),
            ),
        ),
        rx.cond(
            UserState.state == 'song',
            rx.vstack(
                rx.heading("Pick a song!", size="9"),
                rx.cond(
                    UserState.error_message,
                    render_error_message(UserState.error_message),
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Song search",
                        value=UserState.search,
                        on_change=UserState.set_search,
                    ),
                    rx.button(
                        "Search",
                        on_click=UserState.handle_search,
                    ),
                ),
                rx.cond(
                    UserState.search_results,
                    render_search_results(UserState.search_results),
                ),
                rx.button(
                    "Cancel",
                    on_click=UserState.handle_cancel,
                )
            ),
        )
    )


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Your Theme Song!", size="9"),
            rx.hstack(
                rx.cond(
                    State.user,
                    rx.text(f"Hey {State.user['name']}! Playing your theme song: {State.user['song_title']}", size="5"),
                    rx.text("Come up to the camera to play your song!", size="5")
                ),
                rx.cond(
                    State.create_profile,
                    rx.link(
                        rx.text("Click here to create a profile", size="5"),
                        href="/create",
                    ),
                ),
            ),
            rx.hstack(
                webcam_upload_component("123", State.handle_screenshot),
                last_screenshot_widget(State.last_screenshot),
            ),
            justify="center",
            min_height="85vh",
        )
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
    )
)
app.add_page(index, route="/")
app.add_page(create, route="/create")
