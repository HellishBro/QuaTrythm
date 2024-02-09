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
    def from_file(cls, config_file: str):
        with open(config_file) as file:
            json = json5.loads(file.read())

        for key, value in json.items():
            cls.set(key, value)
