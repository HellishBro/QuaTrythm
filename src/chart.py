import pygame as pg

from src.lane import Lane
from src.config import Config
from src.note import TapNote, DragNote

import json5


WinWidth: int = 0
WinHeight: int = 0
def init(sc: pg.Surface):
    global WinWidth, WinHeight
    WinWidth, WinHeight = sc.get_size()

class Chart:
    def __init__(self, lanes: list[Lane]):
        self.lanes = lanes
        self.note_count = sum(len(lane.notes) for lane in self.lanes)

        self.config = Config._()

        self.active_lane = 0

    def update(self, dt: float):
        for lane in self.lanes:
            lane.update(dt)

    def draw(self, sc: pg.Surface):
        pg.draw.rect(sc, (125, 125, 125), ((WinWidth - self.curr_lane.width) / 2, 0, self.curr_lane.width, WinHeight))
        pg.draw.line(sc, (255, 255, 255), (0, self.curr_lane.hit_y), (WinWidth, self.curr_lane.hit_y))

        for lane in self.lanes:
            offset_x = (lane.x - self.curr_lane.x) * lane.width

            surface = pg.Surface((lane.width, WinHeight), pg.SRCALPHA)
            surface.fill((0, 0, 0, 0))
            lane.draw(surface)

            # actual positioning logic
            sc.blit(surface, (offset_x + (WinWidth - lane.width) / 2, 0))

    def keydown(self, ev: pg.Event):
        switches = (self.config.KEY_Lane1, self.config.KEY_Lane2, self.config.KEY_Lane3)
        if ev.key in switches:
            for i, switch in enumerate(switches):
                if ev.key == switch:
                    old_held = self.curr_lane.lanes_held.copy()
                    self.curr_lane.lanes_held = []
                    self.curr_lane.lanes_pressed = []
                    self.curr_lane = i
                    self.curr_lane.lanes_held = old_held

        else:
            self.curr_lane.keydown(ev)

    def keyup(self, ev: pg.Event):
        if ev.key not in (self.config.KEY_Lane1, self.config.KEY_Lane2, self.config.KEY_Lane3):
            self.curr_lane.keyup(ev)

    @property
    def curr_lane(self):
        return self.lanes[self.active_lane]

    @curr_lane.setter
    def curr_lane(self, new: int):
        self.active_lane = new

def parse_chart(file: str) -> Chart:
    with open(file) as f:
        json = json5.loads(f.read())

    json_lanes = json.get('lanes')
    lanes = []
    for i, lane in enumerate(json_lanes):
        lanes.append(Lane([], i, 250))

        for note in lane:
            cls = (TapNote, DragNote)[note[0]]
            x = note[1]
            time = note[2]

            lanes[-1].notes.append(cls(x, time))

        lanes[-1].update_notes()

    return Chart(lanes)
