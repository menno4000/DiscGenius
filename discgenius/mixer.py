#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this script will create a transition between two given songs, using the transition points found by the evaluator
# script. the default transition will occur between two segments defined by the points:
# C, D & E in Song A (points A, B & X in Song B). in these segments the frames of both songs will be manipulated
# with filters (provided by the sound_manipulation.py) and then added up
#
# for manipulating the sound every frame has to be edited. the frames will usually be loaded into a two dimensional list
# or numpy array (2,n), containing two lists of frames per channel (stereo). the input files should already have the
# same bpm values, the analysis class should handle that beforehand.

import datetime
import pprint
import sys

import librosa
import numpy as np

from . import scenarios
from .utility import sound_manipulation as sm
from .utility import utility as util

TSL_LIST = []
SCENARIO = {}
pp = pprint.PrettyPrinter(indent=2)


# Song A with full Bass
def modify_transition_segment_1(frame_array_a, frame_array_b):
    scenario_name = SCENARIO['short_name']
    if scenario_name == "EQ_1.0":
        transition_song_a, transition_song_b = scenarios.EQ_1_segment_1_dynamic(frame_array_a, frame_array_b, SCENARIO)
    elif scenario_name == "EQ_1.1":
        transition_song_a, transition_song_b = scenarios.EQ_1_segment_1_dynamic(frame_array_a, frame_array_b, SCENARIO)
        transition_song_a = sm.cut_bass_for_last_bar(transition_song_a, TSL_LIST[0]/4)
    elif scenario_name == "EQ_2.0":
        transition_song_a = frame_array_a
        transition_song_b = scenarios.low_cut_segment(frame_array_b)
    elif scenario_name == "EQ_2.1":
        transition_song_a = frame_array_a
        transition_song_b = scenarios.low_cut_segment(frame_array_b)
        transition_song_a = sm.cut_bass_for_last_bar(transition_song_a, TSL_LIST[0]/4)
    elif scenario_name == "VFF_1.0":
        transition_song_a, transition_song_b = scenarios.vff_1_segment_1(frame_array_a, frame_array_b, SCENARIO)
    elif scenario_name == "VFF_1.1":
        transition_song_a, transition_song_b = scenarios.vff_1_segment_1(frame_array_a, frame_array_b, SCENARIO)
        transition_song_a = sm.cut_bass_for_last_bar(transition_song_a, TSL_LIST[0]/4)
    elif scenario_name == "CF_1.0":
        transition_song_a, transition_song_b = scenarios.crossfade_segment_1(frame_array_a, frame_array_b, SCENARIO)
    else:
        print("ERROR - Could not find a valid transition scenario.")
        return

    # mix two audio signals
    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# Song B with full Bass
def modify_transition_segment_2(frame_array_a, frame_array_b):
    scenario_name = SCENARIO['short_name']
    if scenario_name == "EQ_1.0":
        transition_song_a, transition_song_b = scenarios.EQ_1_segment_2_dynamic(frame_array_a, frame_array_b, SCENARIO)
    elif scenario_name == "EQ_1.1":
        transition_song_a, transition_song_b = scenarios.EQ_1_segment_2_dynamic(frame_array_a, frame_array_b, SCENARIO)
        transition_song_b = sm.cut_bass_for_last_bar(transition_song_b, TSL_LIST[0])
    elif scenario_name == "EQ_2.0":
        transition_song_a = scenarios.low_cut_segment(frame_array_a)
        transition_song_b = frame_array_b
    elif scenario_name == "EQ_2.1":
        transition_song_a = scenarios.low_cut_segment(frame_array_a)
        transition_song_b = sm.cut_bass_for_last_bar(frame_array_b, TSL_LIST[0])
    elif scenario_name == "VFF_1.0":
        transition_song_a, transition_song_b = scenarios.vff_1_segment_2(frame_array_a, frame_array_b, SCENARIO)
    elif scenario_name == "VFF_1.1":
        transition_song_a, transition_song_b = scenarios.vff_1_segment_2(frame_array_a, frame_array_b, SCENARIO)
        transition_song_b = sm.cut_bass_for_last_bar(transition_song_b, TSL_LIST[0])
    elif scenario_name == "CF_1.0":
        transition_song_a, transition_song_b = scenarios.crossfade_segment_2(frame_array_a, frame_array_b, SCENARIO)
    else:
        print("ERROR - Could not find a valid transition scenario.")
        return

    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# this method will combine the frames of song a & b in two separate time segments (C -- D & D -- E)
def mix_transition_segments(song_a, song_b, frames):
    segment_channels_a = [[], []]
    segment_channels_b = [[], []]

    print("\t\t  Calculating Transition Segment: C -- D, Length in bars: '%s'" % TSL_LIST[0])
    for i in range(frames['between_c_and_d']):
        frame_for_a = frames['until_c'] + i
        frame_for_b = frames['until_a'] + i
        segment_channels_a[0].append(song_a['left_channel'][frame_for_a])
        segment_channels_a[1].append(song_a['right_channel'][frame_for_a])

        segment_channels_b[0].append(song_b['left_channel'][frame_for_b])
        segment_channels_b[1].append(song_b['right_channel'][frame_for_b])

    print("\t\t\tModify Frames of Song A & B for Transition Segment C--D")
    transition_segment_1_left = modify_transition_segment_1(segment_channels_a[0], segment_channels_b[0])
    transition_segment_1_right = modify_transition_segment_1(segment_channels_a[1], segment_channels_b[1])

    # reset
    segment_channels_a = [[], []]
    segment_channels_b = [[], []]

    print("\t\t  Calculating Transition Segment: D -- E, Length in bars: '%s'" % TSL_LIST[1])
    # todo: if e > song length do sth...
    for i in range(frames['between_d_and_e']):
        frame_for_a = frames['until_d'] + i
        frame_for_b = frames['until_b'] + i
        segment_channels_a[0].append(song_a['left_channel'][frame_for_a])
        segment_channels_a[1].append(song_a['right_channel'][frame_for_a])

        segment_channels_b[0].append(song_b['left_channel'][frame_for_b])
        segment_channels_b[1].append(song_b['right_channel'][frame_for_b])

    print("\t\t\tModify Frames of Song A & B for Transition Segment D--E")
    transition_segment_2_left = modify_transition_segment_2(segment_channels_a[0], segment_channels_b[0])
    transition_segment_2_right = modify_transition_segment_2(segment_channels_a[1], segment_channels_b[1])

    print("\t       Adding transition segments 1 & 2 to mix.")
    transition_segment_left = np.append(transition_segment_1_left, transition_segment_2_left)
    transition_segment_right = np.append(transition_segment_1_right, transition_segment_2_right)

    return transition_segment_left, transition_segment_right


def create_mixed_wav_file(config, song_a, song_b, transition_points, frames, tsl_list, mix_name, scenario_name):
    global TSL_LIST
    global SCENARIO
    TSL_LIST = tsl_list
    SCENARIO = util.get_scenario(config, scenario_name)
    sample_rate = config['sample_rate']

    # util.log_info_about_mix(song_a, song_b, transition_points, frames)
    print("INFO - Mixing: Start process of mixing two given songs. Scenario:")
    pp.pprint(SCENARIO)

    if not song_a['frame_rate'] == sample_rate and not song_b['frame_rate'] == sample_rate:
        print(f"ERROR - Skipping mixing because sample rate is not {sample_rate}Hz for both songs.")
        sys.exit()

    print("INFO - Mixing: Adding unmodified frames of song A to mix. Length: '%0.2f's" % transition_points['c'])
    # reading song a just until point C and get all frames for both channels
    song_x = librosa.core.load(song_a['path'], sr=sample_rate, duration=transition_points['c'], mono=False)
    left_mix_channel = song_x[0][0]
    right_mix_channel = song_x[0][1]

    print("INFO - Mixing: Creating transition segments between A & B. Length: '%0.2f's" % (
            transition_points['e'] - transition_points['c']))
    transition_segment_left, transition_segment_right = mix_transition_segments(song_a, song_b, frames)
    left_mix_channel = np.append(left_mix_channel, transition_segment_left)
    right_mix_channel = np.append(right_mix_channel, transition_segment_right)
    del transition_segment_left, transition_segment_right

    print("INFO - Mixing: Adding unmodified frames of song B to mix. Length: '%0.2f's" % (
            song_b['total_frames'] / sample_rate - transition_points['x']))
    transition_time = transition_points['e'] - transition_points['c']
    start_of_b = int(round((transition_points['a'] + transition_time) * sample_rate))
    current_mix = [[], []]
    for i in range(start_of_b, song_b['total_frames']):
        current_mix[0].append(song_b['left_channel'][i])
        current_mix[1].append(song_b['right_channel'][i])

    left_mix_channel = np.append(left_mix_channel, np.asarray(current_mix[0], dtype='float32'))
    right_mix_channel = np.append(right_mix_channel, np.asarray(current_mix[1], dtype='float32'))

    print("INFO - Mixing: Creation of a mix finished. Amount of frames: '%s', Length: '%sm'" % (
        len(left_mix_channel), util.get_length_out_of_frames(config, len(left_mix_channel))))

    mix_array = np.array([left_mix_channel, right_mix_channel], dtype='float32', order='F')

    mix_name += ".wav"
    result_path = f"{config['mix_path']}/{mix_name}"

    util.save_wav_file(config, mix_array, result_path)
    mix_song = {
        'frame_rate': config['sample_rate'],
        'path': result_path,
        'name': mix_name,
        'identifier': 'mix',
        'total_frames': len(mix_array[0]),
        'length': util.get_length_out_of_frames(config, len(mix_array[0]))
    }

    return mix_song
