import pygame as pg

from src.config import Config

TapNoteImg: pg.Surface = None
DragNoteImg: pg.Surface = None

TapNoteSimulImg: pg.Surface = None
DragNoteSimulImg: pg.Surface = None

TapNoteSnd: pg.mixer.Sound = None
DragNoteSnd: pg.mixer.Sound = None

BaseNoteDimensions = (0, 0)

def init():
    global TapNoteImg, DragNoteImg, TapNoteSimulImg, DragNoteSimulImg, TapNoteSnd, DragNoteSnd, BaseNoteDimensions
    TapNoteImg = pg.transform.scale_by(pg.image.load("assets/tap.png").convert_alpha(), Config._().NoteScale)
    DragNoteImg = pg.transform.scale_by(pg.image.load("assets/drag.png").convert_alpha(), Config._().NoteScale)

    TapNoteSimulImg = pg.transform.scale_by(pg.image.load("assets/tap-simul.png").convert_alpha(), Config._().NoteScale)
    DragNoteSimulImg = pg.transform.scale_by(pg.image.load("assets/drag-simul.png").convert_alpha(), Config._().NoteScale)

    BaseNoteDimensions = TapNoteImg.get_size()

    TapNoteSnd = pg.mixer.Sound("assets/tap.wav")
    DragNoteSnd = pg.mixer.Sound("assets/drag.wav")

class Note:
    def __init__(self, x: int, time: float, image: pg.Surface, sound: pg.mixer.Sound):
        self.x = x
        self.time = time

        self.y = 0

        self.image = image
        self.simultaneous = image
        self.sound = sound

        self.w, self.h = self.image.get_size()

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.x}@{self.time}"

    def play_sound(self):
        self.sound.play()

class TapNote(Note):
    def __init__(self, x: int, time: float):
        super().__init__(x, time, TapNoteImg, TapNoteSnd)
        self.simultaneous = TapNoteSimulImg

class DragNote(Note):
    def __init__(self, x: int, time: float):
        super().__init__(x, time, DragNoteImg, DragNoteSnd)
        self.simultaneous = DragNoteSimulImg
