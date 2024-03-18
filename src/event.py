import pygame as pg
import pytweening as tween

WinWidth: int = 0
WinHeight: int = 0
Window: pg.Window = None

def init(sc: pg.Surface, window: pg.Window):
    global WinWidth, WinHeight, Window
    WinWidth, WinHeight = sc.get_size()
    Window = window

EASINGS = [
    tween.linear,
    tween.easeInSine,
    tween.easeOutSine,
    tween.easeInOutSine,
    tween.easeInBack,
    tween.easeOutBack,
    tween.easeInOutBack,
    tween.easeInBounce,
    tween.easeOutBounce,
    tween.easeInOutBounce,
    tween.easeInCirc,
    tween.easeOutCirc,
    tween.easeInOutCirc,
    tween.easeInCubic,
    tween.easeOutCubic,
    tween.easeInOutCubic,
    tween.easeInElastic,
    tween.easeOutElastic,
    tween.easeInOutElastic,
    tween.easeInExpo,
    tween.easeOutExpo,
    tween.easeInOutExpo,
    tween.easeInQuad,
    tween.easeOutQuad,
    tween.easeInOutQuad,
    tween.easeInQuart,
    tween.easeOutQuart,
    tween.easeInOutQuart,
    tween.easeInQuint,
    tween.easeOutQuint,
    tween.easeInOutQuint
]

def ease(function, start, end, percentage):
    return function(percentage) * (end - start) + start

class Event:
    def __init__(self, time, *params):
        self.time = time
        self.params = params
        self.chart = None

    def update(self, dt):
        self.time -= dt

    def remove(self):
        self.chart.events.remove(self)

    def trigger(self, sc: pg.Surface):
        pass

    def chart_loaded(self):
        pass

class LengthedEvent(Event):
    def __init__(self, time, length):
        super().__init__(time, length)
        self.length = length
        self.should_trigger = False

    def update(self, dt):
        super().update(dt)
        if self.time <= 0:
            self.should_trigger = True

        if self.time <= -self.length:
            self.should_trigger = False
            self.remove()

    def trigger(self, sc: pg.Surface):
        pass


class Easeable(LengthedEvent):
    def __init__(self, time, fade_in, hold, fade_out, easing, start_dat, hold_dat, end_dat):
        super().__init__(time, fade_in + hold + fade_out)
        self.easing = EASINGS[easing]
        self.start_dat = start_dat
        self.hold_dat = hold_dat
        self.end_dat = end_dat

        self.fade_in = fade_in
        self.hold = hold
        self.fade_out = fade_out

        self.eased_dat = start_dat

    def ease(self, start, hold, end):
        if -self.time <= self.fade_in:
            percent = -self.time / self.fade_in
            return ease(self.easing, start, hold, percent)
        elif -self.time >= self.fade_in + self.hold:
            percent = (-self.time - self.fade_in - self.hold) / self.fade_out
            return ease(self.easing, end, hold, 1 - percent)
        return hold

    def default_update(self, dt):
        super().update(dt)
        self.eased_dat = self.ease(self.start_dat, self.hold_dat, self.end_dat)



0.
class Grayscale(LengthedEvent):
    def trigger(self, sc: pg.Surface):
        sc.blit(pg.transform.grayscale(sc), (0, 0))

1.
class Invert(LengthedEvent):
    def trigger(self, sc: pg.Surface):
        buf = sc.copy()
        sc.fill((255, 255, 255))
        sc.blit(buf, (0, 0), None, pg.BLEND_SUB)

2.
class Flip(LengthedEvent):
    def __init__(self, time, length, flip_x=False, flip_y=True):
        super().__init__(time, length)
        self.flip_x = flip_x
        self.flip_y = flip_y

    def trigger(self, sc: pg.Surface):
        sc.blit(pg.transform.flip(sc, self.flip_x, self.flip_y), (0, 0))

3.
class RotoZoom(LengthedEvent):
    def __init__(self, time, length, easing, angle, scale):
        super().__init__(time, length)
        self.easing = EASINGS[easing]
        self.angle = angle
        self.scale = scale

        self.starting_angle = 0
        self.starting_scale = 0

        self.set_starting = False

    def update(self, dt):
        super().update(dt)
        percent = -self.time / self.length
        if self.should_trigger:
            if not self.set_starting:
                self.set_starting = True
                self.starting_angle = self.chart.rotation
                self.starting_scale = self.chart.scale

            self.chart.rotation = ease(self.easing, self.starting_angle, self.angle, percent)
            self.chart.scale = ease(self.easing, self.starting_scale, self.scale, percent)

    def remove(self):
        self.chart.rotation = self.angle
        self.chart.scale = self.scale
        super().remove()

4.
class ChromaticAberration(Easeable):

    def trigger(self, sc: pg.Surface):
        red: pg.Surface = sc.copy()
        red.fill(0xFF0000, None, pg.BLEND_MIN)
        green: pg.Surface = sc.copy()
        green.fill(0x00FF00, None, pg.BLEND_MIN)
        blue: pg.Surface = sc.copy()
        blue.fill(0x0000FF, None, pg.BLEND_MIN)
        sc.blit(red, (-self.eased_dat, 0))
        sc.blit(green, (self.eased_dat, -self.eased_dat), None, pg.BLEND_ADD)
        sc.blit(blue, (0, self.eased_dat), None, pg.BLEND_ADD)

5.
class Translate(Easeable):
    """
    +-------100-------+
    |                 |
    |                 |
    -100  (0, 0)      100
    |                 |
    |                 |
    +----- -100 ------+
    """

    def update(self, dt):
        super().update(dt)
        ease_x = self.ease(self.start_dat[0], self.hold_dat[0], self.end_dat[0])
        ease_y = self.ease(self.start_dat[1], self.hold_dat[1], self.end_dat[1])
        self.chart.translate = (ease_x / 100 * WinWidth, ease_y / 100 * WinHeight)



ALL_EVENTS = [
    Grayscale, Invert, Flip, RotoZoom, ChromaticAberration, Translate
]