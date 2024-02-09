import pygame as pg

from src.config import Config
from src.note import Note, TapNote, DragNote

BaseNoteWidth: int = 0
BaseNoteHeight: int = 0
WinWidth: int = 0
WinHeight: int = 0

def init(sc: pg.Surface):
    global BaseNoteWidth, BaseNoteHeight, WinWidth, WinHeight
    from src.note import BaseNoteDimensions as BND
    BaseNoteWidth, BaseNoteHeight = BND
    WinWidth, WinHeight = sc.get_size()

class Lane:
    def __init__(self, notes: list[Note], x: int, speed: float):
        self.notes = notes

        self.config = Config._()

        self.x = x
        self.speed = speed

        self.scroll = -self.speed * 2

        self.lanes_held = []
        self.lanes_pressed = []

        for note in self.notes:
            note.y = note.time * self.speed

        self.score = 0

        self.width = BaseNoteWidth * 4

    def update_notes(self):
        for note in self.notes:
            note.y = note.time * self.speed

    def __repr__(self):
        return f"Lane{self.notes}"

    def update(self, dt: float):
        self.scroll += dt * self.speed

        pops = []
        for i, note in enumerate(self.notes):
            note.y -= self.speed * dt
            if note.x in self.lanes_pressed and isinstance(note, TapNote):
                time_offset = abs(note.y / self.speed)
                if time_offset <= 0.08:
                    self.score += 1
                elif time_offset <= 0.16:
                    self.score += 0.65
                else:
                    continue

                pops.insert(0, i)
                self.lanes_pressed.remove(note.x)
            elif note.x in self.lanes_held and isinstance(note, DragNote):
                if note.y <= 0 and abs(note.y / self.speed) < 0.16:
                    pops.insert(0, i)

        pops.reverse()
        for i in pops:
            self.notes[i].play_sound()
            del self.notes[i]

        self.lanes_pressed = []

    def draw(self, sc: pg.Surface):
        for note in self.notes:
            sc.blit(note.image, (self.note_x(note.x), self.hit_y - note.y - note.h / 2))

    def keydown(self, ev: pg.Event):
        valid = (self.config.KEY_Note1, self.config.KEY_Note2, self.config.KEY_Note3, self.config.KEY_Note4)
        for i, k in enumerate(valid):
            if ev.key == k:
                self.lanes_held.append(i)
                self.lanes_pressed.append(i)

    def keyup(self, ev: pg.Event):
        valid = (self.config.KEY_Note1, self.config.KEY_Note2, self.config.KEY_Note3, self.config.KEY_Note4)
        for i, k in enumerate(valid):
            if ev.key == k and i in self.lanes_held:
                self.lanes_held.remove(i)

    def note_x(self, note):
        return note * BaseNoteWidth

    @property
    def hit_y(self):
        return int(WinHeight * 0.9)
