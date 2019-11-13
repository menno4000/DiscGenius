#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this script will execute a transition between two given songs, using the transition points found by the evaluator script
# the default transition will occur between two segments defined by the points: C, D & E in Song A (points A, B & X in Song B)
# in these segments the frames of both songs will be manipulated with filters (provided by the sound_manipulation.py) and then added up
#
# for manipulating the sound every frame has to be edited
# the frames will usually be loaded into a two dimensional list or numpy array (2,n), containing two lists of frames per channel (stereo)
# the input files should already have the same bpm values, the analysis class should handle that beforehand

__author__ = "Oskar Sailer"

import os
import sys

import numpy as np
import librosa

import evaluator
import scenarios
import utility as util

SAMPLE_RATE = 44100

TSL_LIST = []


# Song A with full Bass
def modify_transition_segment_1(frame_array_a, frame_array_b):
    transition_song_a, transition_song_b = scenarios.transition_scenario_2_segment_1_dynamic(frame_array_a,
                                                                                             frame_array_b, TSL_LIST[0])

    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# Song B with full Bass
def modify_transition_segment_2(frame_array_a, frame_array_b):
    transition_song_a, transition_song_b = scenarios.transition_scenario_2_segment_2_dynamic(frame_array_a,
                                                                                             frame_array_b, TSL_LIST[1])

    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# this method will combine the frames of song a & b in two separate time segments (C -- D & D -- E)
def mix_transition_segments(song_a, song_b, transition_points, frames):
    segment_channels_a = [[], []]
    segment_channels_b = [[], []]

    print("INFO -   Calculating Transition Segment: C -- D, Length in bars: '%s'" % TSL_LIST[0])
    for i in range(frames['between_c_and_d']):
        frame_for_a = frames['until_c'] + i
        frame_for_b = frames['until_a'] + i
        segment_channels_a[0].append(song_a['left_channel'][frame_for_a])
        segment_channels_a[1].append(song_a['right_channel'][frame_for_a])

        segment_channels_b[0].append(song_b['left_channel'][frame_for_b])
        segment_channels_b[1].append(song_b['right_channel'][frame_for_b])

    print("INFO -       Modify Frames of Song A & B for Transition Segment C--D")
    transition_segment_1_left = modify_transition_segment_1(segment_channels_a[0], segment_channels_b[0])
    transition_segment_1_right = modify_transition_segment_1(segment_channels_a[1], segment_channels_b[1])

    # reset
    segment_channels_a = [[], []]
    segment_channels_b = [[], []]

    print("INFO -   Calculating Transition Segment: D -- E, Length in bars: '%s'" % TSL_LIST[1])
    # todo: if e > song length do sth...
    for i in range(frames['between_d_and_e']):
        frame_for_a = frames['until_d'] + i
        frame_for_b = frames['until_b'] + i
        segment_channels_a[0].append(song_a['left_channel'][frame_for_a])
        segment_channels_a[1].append(song_a['right_channel'][frame_for_a])

        segment_channels_b[0].append(song_b['left_channel'][frame_for_b])
        segment_channels_b[1].append(song_b['right_channel'][frame_for_b])

    print("INFO -       Modify Frames of Song A & B for Transition Segment D--E")
    transition_segment_2_left = modify_transition_segment_2(segment_channels_a[0], segment_channels_b[0])
    transition_segment_2_right = modify_transition_segment_2(segment_channels_a[1], segment_channels_b[1])

    print("INFO - Adding transition segments 1 & 2 to mix.")
    transition_segment_left = np.append(transition_segment_1_left, transition_segment_2_left)
    transition_segment_right = np.append(transition_segment_1_right, transition_segment_2_right)

    return transition_segment_left, transition_segment_right


def create_mixed_wav_file(song_a, song_b, transition_points, paths, frames, tsl_list):
    global TSL_LIST
    TSL_LIST = tsl_list

    util.log_info_about_mix(song_a, song_b, transition_points, frames)
    print("INFO - Keep calm... Mixing both audiofiles.")

    if not song_a['frame_rate'] == 44100 and not song_b['frame_rate'] == 44100:
        print("ERROR - Skipping mixing because sample rate is not 44.100Hz for both songs.")
        sys.exit()

    print("INFO - Adding unmodified frames of song A to mix. Length: '%0.2f's" % transition_points['c'])
    # reading song a just until point C and get all frames for both channels
    song_x = librosa.core.load(song_a['path'], sr=evaluator.SAMPLE_RATE, mono=False, duration=transition_points['c'])
    left_mix_channel = song_x[0][0]
    right_mix_channel = song_x[0][1]

    print("INFO - Creating transition segments between A & B. Length: '%0.2f's" % (
            transition_points['e'] - transition_points['c']))
    transition_segment_left, transition_segment_right = mix_transition_segments(song_a, song_b, transition_points,
                                                                                frames)
    left_mix_channel = np.append(left_mix_channel, transition_segment_left)
    right_mix_channel = np.append(right_mix_channel, transition_segment_right)
    del transition_segment_left, transition_segment_right

    print("INFO - Adding unmodified frames of song B to mix. Length: '%0.2f's" % (
            song_b['total_frames'] / evaluator.SAMPLE_RATE - transition_points['x']))
    transition_time = transition_points['e'] - transition_points['c']
    start_of_b = int(round((transition_points['a'] + transition_time) * evaluator.SAMPLE_RATE))
    current_mix = [[], []]
    for i in range(start_of_b, song_b['total_frames']):
        current_mix[0].append(song_b['left_channel'][i])
        current_mix[1].append(song_b['right_channel'][i])

    left_mix_channel = np.append(left_mix_channel, np.asarray(current_mix[0], dtype='float32'))
    right_mix_channel = np.append(right_mix_channel, np.asarray(current_mix[1], dtype='float32'))

    if os.path.exists(paths['result_path']):
        print("INFO - Removing old file...")
        os.remove(paths['result_path'])

    print("INFO - Creation of a mix finished. Amount of frames: '%s', Length: '%sm'" % (
        len(left_mix_channel), util.get_length_out_of_frames(len(left_mix_channel))))
    return np.array([left_mix_channel, right_mix_channel], dtype='float32', order='F')
