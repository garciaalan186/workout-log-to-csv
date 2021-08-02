# -*- coding: utf-8 -*-

import re
import itertools
import sys

import pandas

wo_log_input_path = sys.argv[1]
wo_log_csv_export_path = sys.argv[2]

with open(wo_log_input_path, 'r') as wo_log_f:
    wo_log_str = wo_log_f.read()

# function declarations
# todo: refactor as class, make more modular and extensible (e.g. RIR etc)

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


def flatten_output_list(input_list):
    if list not in [type(item) for item in input_list[0]]:
        return input_list
    else:
        return flatten_output_list(list(itertools.chain.from_iterable(input_list)))

# get workout day text bodies
woday_bodies = get_woday_bodies(wo_log_str)

# get session bodies for workout day text
session_list = list(map(get_session_bodies, woday_bodies))

# get volume data
vol_weight_list = list(map(get_vol_weight_reps, session_list))

# flatten nested output list
flattened_output_list = flatten_output_list(vol_weight_list)

# create dataframe
output_df = pandas.DataFrame(flattened_output_list)

# export to csv
# todo: make columns vary based on rep or set tracking
output_df.columns = ["Date", "Session", "Exercise", "Weight", "Set Reps", "Notes"]
output_df.to_csv(wo_log_csv_export_path, index=False)
