import json5
import random

dict = {"lanes": [[], [], []], "song": "test.mp3", "name": "Creo - Dimensions", "difficulty": "5.6", "bpm": 115, "background": "test.jpg"}

t = 0
for x in [random.randint(0, 2) for _ in range(15)]:
    amt = random.randint(25, 40)
    for _ in range(amt):
        z = random.randint(0, 3)
        dict["lanes"][x].append([random.randint(0, random.randint(0, 1)), z, t])
        if random.randint(0, 10) == 0:
            while (new := random.randint(0, 3)) == z:
                pass

            dict["lanes"][x].append([random.randint(0, random.randint(0, 1)), new, t])

        t += 0.25 * random.randint(1, 4)
    t += 1

with open("test.json5", "w+") as f:
    f.write(json5.dumps(dict))
