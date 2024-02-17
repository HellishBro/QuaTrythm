import json5
import zipfile
import os

osz = input("OSZ file: ")
with zipfile.ZipFile(osz) as zf:
    for file in zf.filelist:
        if file.filename.endswith(".osu"):
            chart = file

    with zf.open(chart) as f:
        osu = f.read().decode().split("\n")
        for i, line in enumerate(osu):
            osu[i] = line.replace("\r", "")

bpm = int(input("Enter BPM: "))

out = {}

def get_line(phrase):
    for num, line in enumerate(osu, 0):
        if phrase in line:
            return num

out['metadata'] = {}
out['hitobjects'] = []

metadata_line = get_line('[Metadata]')
difficulty_line = get_line('[Difficulty]')
hit_line = get_line('[HitObjects]')

metadata_list = osu[metadata_line:difficulty_line-1]
hitobject_list = osu[hit_line:]

for item in metadata_list:
    if ':' in item:
        item = item.split(':')
        out['metadata'][item[0]] = item[1][1:]

for item in hitobject_list:
    if ',' in item:
        item = item.split(',')
        point = {
            'x': int(int(item[0]) // (512 / 4)),
            'time': round((int(item[2]) / 1000) / (60 / bpm), 3),
            'switch_lane': bool(int(item[4]) & 8),
            'drag': bool(int(item[4]) & 2),
        }

        out['hitobjects'].append(point)

directory = out["metadata"]["Title"]
difficulty = input("Difficulty: ")

lanes = [[], [], []]
curr_lane = 0

for note in out['hitobjects']:
    if note['switch_lane']:
        curr_lane = int(input("Which lane to switch to: "))

    lanes[curr_lane].append([int(note['drag']), note['x'], note['time']])

output = {
    "lanes": lanes,
    "name": input("Chart Name: "),
    "difficulty": difficulty,
    "bpm": bpm
}

if not os.path.exists(directory):
    os.mkdir(output['name'])

with open(directory + '/chart.json5', 'w+') as f:
    f.write(json5.dumps(output, indent=2))