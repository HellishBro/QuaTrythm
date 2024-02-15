import os.path

import pygame as pg

import json5

class Config:
    INSTANCE: 'Config' = None

    def __init__(self):
        self.KEY_Note1 = pg.K_d
        self.KEY_Note2 = pg.K_f
        self.KEY_Note3 = pg.K_j
        self.KEY_Note4 = pg.K_k
        self.KEY_Lane1 = pg.K_v
        self.KEY_Lane2 = pg.K_b
        self.KEY_Lane3 = pg.K_n

        self.NoteScale = 1

        self.VOLUME_Music = 1
        self.VOLUME_Sound = 1

        self.BGDim = 125

    @staticmethod
    def _() -> 'Config':
        if Config.INSTANCE is None:
            Config.INSTANCE = Config()

        return Config.INSTANCE

    @staticmethod
    def set(key: str, value):
        setattr(Config._(), key, value)

    @staticmethod
    def get(key: str):
        return getattr(Config._(), key)

    @classmethod
    def load(cls):
        if os.path.exists("user/config.json5"):
            with open("user/config.json5") as file:
                json = json5.loads(file.read())

            for key, value in json.items():
                Config._().set(key, value)

        return Config._()

    def save(self):
        attrs = {}
        for k, v in self.__dict__.items():
            if not (k.startswith('__') or callable(getattr(self, k))):
                attrs[k] = v

        with open("user/config.json5", "w+") as file:
            file.write(json5.dumps(attrs))
