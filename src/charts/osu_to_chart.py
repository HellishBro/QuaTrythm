import json5
import zipfile
import os
import math

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
        x = int(int(item[0]) * 5 / 512)
        time = (int(item[2]) / 1000) / (60 / bpm)
        if x < 4:
            point = {
                'type': 'note',
                'x': x,
                'time': time,
                'switch_lane': bool(int(item[4]) & 8),
                'drag': bool(int(item[4]) & 2),
            }
        else:
            point = {
                'type': 'event',
                'time': time,
                'event_type': 0,
                'params': []
            }

        out['hitobjects'].append(point)

directory = out["metadata"]["Title"]
difficulty = input("Difficulty: ")

lanes = [[], [], []]
curr_lane = 0

events = []

for note in out['hitobjects']:
    if note['type'] == 'note':
        if note['switch_lane']:
            curr_lane = int(input("Which lane to switch to: "))

        lanes[curr_lane].append([int(note['drag']), note['x'], note['time']])
    elif note['type'] == 'event':
        events.append([note['time'], note['event_type'], note['params']])

output = {
    "lanes": lanes,
    "events": events,
    "name": input("Chart Name: "),
    "difficulty": difficulty,
    "bpm": bpm
}

if not os.path.exists(directory):
    os.mkdir(output['name'])

with open(directory + '/chart.json5', 'w+') as f:
    f.write(json5.dumps(output, indent=2))