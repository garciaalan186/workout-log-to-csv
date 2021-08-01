# -*- coding: utf-8 -*-

import re
import pandas
import itertools
wo_log_str = """d 7/20/2021
s shoulder day
e upright row
v 70: 12 10 9 rest was too short 8 7 lorem ipsum
e cable lateral raise
v 20: 15 13 10 10 9
v 10: 12 9

d 7/21/2021
s back
e bent row
v 220: 16 14 13 11 10
"""

csv_export_arr = []

lines = wo_log_str.splitlines()
len_lines = len(lines)

def get_woday_bodies(str):
    split_wodays = re.split(r"d (.*)\n", str)[1:]
    return list(zip(*(iter(split_wodays),) * 2))

def get_session_bodies(tuple_str):
    split_session_bodies = re.split(r"e (.*)\n", tuple_str[1])
    return tuple_str[0], split_session_bodies[0], list(zip(*(iter(split_session_bodies[1:]),) * 2))

def process_volume_reps(vol_rep_str):
    # split by \d+ ?(.*)
    return re.findall(r"(\d+) ([ |A-Za-z]+ ?)?", vol_rep_str)

def get_volume_bodies(volume_tuple):
    vol_match = re.match(r"v (.*)\n", volume_tuple[3])
    if vol_match:
        vol_str = vol_match.group(1)
        vol_weight_str = re.match(r"(\d+):", vol_str).group(1)
        vol_reps_str = re.match(r"(\d+): (.*)", vol_str).group(2)
        vol_reps_list = process_volume_reps(vol_reps_str)

        return [[volume_tuple[0], volume_tuple[1].title(), str(volume_tuple[2]).title(), vol_weight_str, vol_rep[0], vol_rep[1].capitalize()] for vol_rep in vol_reps_list]

def get_vol_weight_reps(tuple_str):
    exercise_list = [[tuple_str[0], tuple_str[1][2:-1], exercise[0], exercise[1]] for exercise in tuple_str[2]]
    volume_list = list(map(get_volume_bodies, exercise_list))
    return volume_list

woday_bodies = get_woday_bodies(wo_log_str)
session_list = list(map(get_session_bodies, woday_bodies))
# print(session_list)

vol_weight_list = list(map(get_vol_weight_reps, session_list))

def flatten_output_list(input_list):
    if list not in [type(item) for item in input_list[0]]:
        return input_list
    else:
        return flatten_output_list(list(itertools.chain.from_iterable(input_list)))

flattened_output_list = flatten_output_list(vol_weight_list)

output_df = pandas.DataFrame(flattened_output_list)
output_df.columns = ["Date", "Session", "Exercise", "Weight", "Set Reps", "Notes"]
print(output_df)
output_df.to_csv("workout_log_export.csv", index=False)
