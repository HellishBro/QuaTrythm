import json5

with open(input("file: ")) as f:
    content = f.read()

dict = {"lanes": [[], [], []]}
content = content.split("[HitObjects]\n")[1]

for line in content.split("\n"):
    if line:
        toks = line.split(",")
        x, y, time, *_ = toks

        dict["lanes"][0].append([0, int(int(x) / 512 * 4), float(time) / 1000])

with open(input("output file: "), "w+") as f:
    json5.dump(dict, f)
