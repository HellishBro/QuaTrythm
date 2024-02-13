import json5
import os

class User:
    INSTANCE: 'User' = None

    def __init__(self):
        self.song_scores = {}
        self.fc = []

    def set_score(self, id, score):
        if self.song_scores.get(id, 0) < score:
            self.song_scores[id] = score

    def get_score(self, id) -> int:
        return self.song_scores.get(id, 0)

    def set_fc(self, id):
        self.fc.append(id)

    def get_fc(self, id) -> bool:
        return id in self.fc

    @property
    def json(self):
        base_dict = {
            "clears": {},
            "fc": self.fc
        }
        for id, score in self.song_scores.items():
            base_dict["clears"][id] = score

        return base_dict

    @classmethod
    def _(cls) -> 'User':
        if User.INSTANCE is None:
            User.INSTANCE = User()

        return User.INSTANCE

    def save(self):
        if not os.path.exists("user"):
            os.mkdir("user")
        with open("user/save.json5", "w+") as f:
            f.write(json5.dumps(self.json))

    @classmethod
    def load(cls):
        if not os.path.exists("user/save.json5"):
            User.INSTANCE = User()

        else:
            clazz = User()
            with open("user/save.json5") as f:
                data = json5.loads(f.read())

            clears: dict = data["clears"]
            for id, score in clears.items():
                clazz.song_scores[int(id)] = score

            clazz.fc = data["fc"]

            User.INSTANCE = clazz

        return User._()
