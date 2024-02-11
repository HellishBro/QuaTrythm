import pygame as pg

from src.chart import Chart
from src.lane import Lane
from src.utils import gradient, render_text

from enum import Enum, auto
from random import choice
import math

class Ranks(Enum):
    AP = auto()
    FC = auto()
    V = auto()
    S = auto()
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    F = auto()

# endscreen remarks
remarks = {
    Ranks.F: [
        "Congratulations, you've unlocked the 'Dirt Devourer' achievement!",
        "Failing like a pro - only a true master can achieve this level of art.",
        "In the world of gaming, you're a pioneer of dirt exploration.",
        "Failures like yours should be preserved in a museum. So historic!",
        "!This program cannot be run in Dirt mode.",
        "Do you want to open the dirt guide now?"
    ],
    Ranks.D: [
        "Skill issues detected. Would you like a tutorial on pressing buttons?",
        "Just a little better than failing – you've set the bar astronomically low!",
        "Skill issues level: Expert. Keep pushing those wrong buttons!",
        "Failing with such finesse, it's almost impressive. Almost."
    ],
    Ranks.C: [
        "Nice gaming chair, does it come with a 'Git Gud' upgrade?",
        "Grinding time? More like, 'time to reconsider your life choices.'",
        "Your gaming chair must have a 'Lose More' setting.",
        "Mom said it's my turn.",
        "Do or do not. There is no try",
        "You cannot chart a AP if the missing has a error."
    ],
    Ranks.B: [
        "Almost passed – the keyword here is 'almost.'",
        "This game needs more playtime, and you need more skilltime.",
        "Playstyle marked as spam",
        "BEHOLD! A snarky remark!"
    ],
    Ranks.A: [
        "... Passing. Next time, aim for the sky.",
        "Absolutely splendid. Next song unlocked.",
        "What if I tweaked the next simulation?",
        "This message is extremely rare."
    ],
    Ranks.S: [
        "Wow! Epic!",
        "Impressive!",
        "I honestly did not expect you to make it this far.",
        "You know that the timing window is very forgiving right?",
        "...After a mental breakdown... I present to you:"
    ],
    Ranks.V: [
        "Absolutely insane! Why though?",
        "Truly an S+ moment.",
        "Launching secret OS...",
        "Well done... now try to complete it without any misses!",
        "I cant hear the music."
    ],
    Ranks.FC: [
        "Full combo! Zero miss! Not perfect! Try harder!",
        "Now do it without torturing yourself! (Impossible)",
        "You cannot AP a chart if it have a small error",
        "Timing could be better."
    ],
    Ranks.AP: [
        "What IS your reaction time?! GG!",
        "Absolutely insane++! Please someone check if the game's broken or if you are a masochist.",
        "Reflex Master!",
        "Sorry I fell asleep. Do it again?",
        "Not impressive I beat that in like 2 seconds",
        "BUT BRO, DO YOU EVEN LIFT!?"
    ]
}

rank_colors = {
    Ranks.F: (50, 50, 50, 125),
    Ranks.D: (100, 100, 100, 125),
    Ranks.C: (125, 125, 125, 125),
    Ranks.B: (150, 150, 150, 125),
    Ranks.A: (125, 255, 125, 125),
    Ranks.S: (50, 255, 10, 125),
    Ranks.V: (0, 255, 125, 125),
    Ranks.FC: (0, 255, 255, 125),
    Ranks.AP: (255, 255, 0, 125)
}

ImgF: pg.Surface = None
ImgD: pg.Surface = None
ImgC: pg.Surface = None
ImgB: pg.Surface = None
ImgA: pg.Surface = None
ImgS: pg.Surface = None
ImgV: pg.Surface = None
ImgFC: pg.Surface = None
ImgAP: pg.Surface = None

WinWidth, WinHeight = (0, 0)

def init(sc: pg.Surface):
    global ImgF, ImgD, ImgC, ImgB, ImgA, ImgS, ImgV, ImgFC, ImgAP, WinWidth, WinHeight
    ImgF = pg.image.load("assets/grade/f.png").convert_alpha()
    ImgD = pg.image.load("assets/grade/d.png").convert_alpha()
    ImgC = pg.image.load("assets/grade/c.png").convert_alpha()
    ImgB = pg.image.load("assets/grade/b.png").convert_alpha()
    ImgA = pg.image.load("assets/grade/a.png").convert_alpha()
    ImgV = pg.image.load("assets/grade/v.png").convert_alpha()
    ImgS = pg.image.load("assets/grade/s.png").convert_alpha()
    ImgFC = pg.image.load("assets/grade/fc.png").convert_alpha()
    ImgAP = pg.image.load("assets/grade/ap.png").convert_alpha()

    WinWidth, WinHeight = sc.get_size()

class ResultScreen:
    def __init__(self, chart: Chart):
        self.chart = chart
        pg.mixer.music.fadeout(10000)

        self.rank = Ranks.F
        if self.chart.score >= 600_000:
            self.rank = Ranks.D
        if self.chart.score >= 700_000:
            self.rank = Ranks.C
        if self.chart.score >= 820_000:
            self.rank = Ranks.B
        if self.chart.score >= 880_000:
            self.rank = Ranks.A
        if self.chart.score >= 920_000:
            self.rank = Ranks.S
        if self.chart.score >= 960_000:
            self.rank = Ranks.V
        if self.chart.combo == self.chart.note_count:
            self.rank = Ranks.FC
        if self.chart.score == 1_000_000:
            self.rank = Ranks.AP

        self.rank_img: pg.Surface = None
        match self.rank:
            case Ranks.F: self.rank_img = ImgF
            case Ranks.D: self.rank_img = ImgD
            case Ranks.C: self.rank_img = ImgC
            case Ranks.B: self.rank_img = ImgB
            case Ranks.A: self.rank_img = ImgA
            case Ranks.S: self.rank_img = ImgS
            case Ranks.V: self.rank_img = ImgV
            case Ranks.FC: self.rank_img = ImgFC
            case Ranks.AP: self.rank_img = ImgAP

        self.rank_img = pg.transform.scale_by(self.rank_img, 0.75)

        self.bg = gradient((0, 0, 0, 0), rank_colors[self.rank], 0, (WinWidth, WinHeight), pg.SRCALPHA)

        self.score_text = render_text(f"{self.chart.score:,}", 50, (255, 255, 255))
        remark = choice(remarks[self.rank])
        self.remark_text = render_text(remark, 30, (255, 255, 255), WinWidth // 4 * 3)

        self.max_combo_text = render_text("Max Combo:", 30, (255, 255, 255))
        self.max_combo = render_text(f"{self.chart.max_combo:,}", 25, (255, 255, 255))
        self.combo_x = 10

        self.average_error_text = render_text("Average Error:", 30, (255, 255, 255))
        if len(self.chart.accuracy_offsets) > 0:
            average_error = sum(self.chart.accuracy_offsets) / len(self.chart.accuracy_offsets)
        else:
            average_error = 0
        self.average_error = render_text(f"{round(average_error * 1000)}ms", 25, (255, 255, 255))
        self.error_x = 110

        self.time = 0

        self.bg_alpha = 0

    @staticmethod
    def l(x, a):
        if x > a: return 1
        else:
            return (-math.cos(x * math.pi / a) + 1) / 2

    def update(self, dt: float):
        self.time += dt
        self.combo_x = math.fabs(math.cos(self.time * math.pi)) * 100 + 10
        self.error_x = math.fabs(math.sin(self.time * math.pi)) * 100 + 10
        self.bg_alpha = 230 * self.l(self.time, 5) + 12.5 * (1 - math.cos(2 * math.pi * self.time))

    def draw(self, sc: pg.Surface):
        sc.blit(self.chart.background, ((WinWidth - self.chart.background.get_width()) / 2, (WinHeight - self.chart.background.get_height()) / 2))

        self.bg.set_alpha(self.bg_alpha)
        sc.blit(self.bg, (0, 0))

        sc.blit(self.rank_img, ((WinWidth - self.rank_img.get_width()) / 2, (WinHeight - self.rank_img.get_height()) / 2))
        sc.blit(self.score_text, ((WinWidth - self.score_text.get_width()) / 2, (WinHeight - self.rank_img.get_height()) / 2 - self.score_text.get_height() - 25))
        sc.blit(self.remark_text, ((WinWidth - self.remark_text.get_width()) / 2, (WinHeight / 2) + self.rank_img.get_height() / 2 + 25))

        sc.blit(self.max_combo_text, (self.combo_x, WinHeight // 4))
        sc.blit(self.max_combo, (self.combo_x, WinHeight // 4 + self.max_combo_text.get_height() + 5))

        sc.blit(self.average_error_text, (self.error_x, WinHeight // 4 * 2))
        sc.blit(self.average_error, (self.error_x, WinHeight // 4 * 2 + self.average_error_text.get_height() + 5))

        summary_perfect = render_text(f"Perfect: {self.chart.perfects:,}", 24, (255, 255, 0))
        summary_good = render_text(f"Good: {self.chart.goods:,}", 24, (0, 125, 255))
        summary_bad = render_text(f"Bad: {self.chart.bads:,}", 24, (255, 255, 255))
        summary_early = render_text(f"Early: {self.chart.early:,}", 24, (0, 255, 255))
        summary_late = render_text(f"Late: {self.chart.late:,}", 24, (0, 125, 125))

        y = 25
        sc.blit(summary_perfect, (WinWidth - summary_perfect.get_width() - 25, y))
        y += summary_perfect.get_height() + 10
        sc.blit(summary_good, (WinWidth - summary_good.get_width() - 25, y))
        y += summary_good.get_height() + 10
        sc.blit(summary_bad, (WinWidth - summary_bad.get_width() - 25, y))
        y += summary_bad.get_height() + 10
        sc.blit(summary_early, (WinWidth - summary_early.get_width() - 25, y))
        y += summary_early.get_height() + 10
        sc.blit(summary_late, (WinWidth - summary_late.get_width() - 25, y))

    def keyup(self, ev: pg.Event):
        pass

    def keydown(self, ev: pg.Event):
        pass
