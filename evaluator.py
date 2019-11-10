#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this script will execute a transition between two given songs, using the data provided by the analysis script
# the input files should already have the same bpm values, the analysis class should handle that beforehand
# wav files will be read & written with the librosa module
# for manipulating the sound every frame has to be edited
# the frames will usually be loaded into a two dimensional array (2,n), containing two lists of frames per channel (stereo)
# the default transition will occur between two segments defined by the points: C, D & E in Song A (A, B & X in Song B)
# in these segments the frames of both songs will be manipulated with filters and then added up.

__author__ = "Oskar Sailer"

import os
import time
import sys

import librosa
import numpy as np
import matplotlib.pyplot as plt
import sound_manipulation as sm

# 2 bytes pro kanal, 2 kanäle, da stereo --> 4 bytes pro frame
# np.column_stack um zwei channel-listen in tupel zu verwandeln
# variables will be imported from csv file, provided by analysis

SAMPLE_RATE = 44100

# vff = volume fading factor
VFF_1 = 0.8
VFF_2 = 0.7
VFF_3 = 0.6
VFF_4 = 0.50

# TSL = Transition Segment Length
TSL_1 = 48
TSL_2 = 16


def get_length_out_of_frames(amount_of_frames, samplerate=SAMPLE_RATE):
    length_in_seconds = amount_of_frames / samplerate
    array = str(length_in_seconds / 60).split('.')
    minutes = int(array[0])
    seconds = int(60 / 100 * int(array[1][0:2]))
    return "%s:%s" % (minutes, seconds)


def log_info_about_mix(song_a, song_b, transition_points, frames):
    rest_frames_song_a = song_a['total_frames'] - frames['until_e']
    rest_frames_song_b = song_b['total_frames'] - frames['until_x']

    print(
        "------------------------------------------------------------------------------------------------------------------------")
    print("INFO - Mix setup:")
    print("Song A:      ..........................c.............d. . . . . . e________")
    print("Song B:                ________________a. . . . . . .b............x..............")
    print("In seconds:")
    print("Song A:    ..........................%0.2f........%0.2f. . . . .%0.2f________________" % (
        transition_points['c'], transition_points['d'], transition_points['e']))
    print("Song B:                ______________%0.2f. . . . . .%0.2f.........%0.2f..........." % (
        transition_points['a'], transition_points['b'], transition_points['x']))
    print("In frames:")
    print("Song A:       .....%s.....%s.....%s.....%s....." % (
    frames['until_c'], frames['between_c_and_d'], frames['between_d_and_e'], rest_frames_song_a))
    print("Song B:         .....%s.....%s.....%s.....%s....." % (
    frames['until_a'], frames['between_c_and_d'], frames['between_d_and_e'], rest_frames_song_b))
    print("Total:     ............................%s......................................" % (
            frames['until_c'] + frames['between_c_and_d'] + frames['between_d_and_e'] + rest_frames_song_b))
    print(
        "------------------------------------------------------------------------------------------------------------------------")
    print()


def plot_audio_channel(audio_channel):
    plt.plot(audio_channel)
    plt.ylabel('audio channel')
    plt.show()


def calculate_frames(song_a, song_b, transition_points):
    frames = {
        'complete_song_a': song_a['total_frames'],
        'complete_song_b': song_b['total_frames'],
        'until_a': int(round(transition_points['a'] * SAMPLE_RATE)),
        'until_b': int(round(transition_points['b'] * SAMPLE_RATE)),
        'until_x': int(round(transition_points['x'] * SAMPLE_RATE)),
        'until_c': int(round(transition_points['c'] * SAMPLE_RATE)),
        'until_d': int(round(transition_points['d'] * SAMPLE_RATE)),
        'until_e': int(round(transition_points['e'] * SAMPLE_RATE)),
        'between_c_and_d': int(round((transition_points['d'] - transition_points['c']) * SAMPLE_RATE)),
        'between_d_and_e': int(round((transition_points['e'] - transition_points['d']) * SAMPLE_RATE))
    }
    return frames


def read_wav_file(filepath, duration=None):
    # alternatives: soundfile, wav, sciPy, pydub
    # oder pydub nutzen? https://stackoverflow.com/questions/37999150/python-how-to-split-a-wav-file-into-multiple-wav-files/43367691
    print("INFO - Reading song '%s'" % filepath)

    librosa_load = librosa.core.load(filepath, sr=SAMPLE_RATE, mono=False, duration=duration)
    song = {'frames': librosa_load[0],
            'left_channel': librosa_load[0][0],
            'right_channel': librosa_load[0][1],
            'frame_rate': librosa_load[1],
            'path': filepath
            }
    song['total_frames'] = len(song['frames'][0])
    song['length'] = get_length_out_of_frames(song['total_frames'])

    print("INFO - Parameters: Framerate '%s', Total Frames '%s', Length '%sm'\n" % (
        song['frame_rate'], song['total_frames'], song['length']))
    return song


def save_wav_file(list_of_frames, path, samplerate=SAMPLE_RATE):
    # todo: filesize doubled because bits per sample doubled
    # write with soundfile? https://github.com/bastibe/SoundFile/issues/203, format wrong: (channels x frames) --> (channels, frames)
    #
    print("INFO - Saving resulting audiofile to '%s'" % path)
    librosa.output.write_wav(path, list_of_frames, samplerate, norm=True)
    print("SUCCESS - Finished saving.")
    # sf.write(path, list_of_frames, samplerate, subtype='FLOAT', format='WAV')
    # scipy.io.wavfile.write(path, samplerate, list_of_frames)


# Song A with full Bass
def modify_transition_segment_1(frame_array_a, frame_array_b):

    # --- modifying Song A ---
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a)//2]
    frame_array_a_2 = frame_array_a[len(frame_array_a)//2:]

    # slowly decrease volume of Song A
    frame_array_a_1 = sm.edit_volume_by_factor(frame_array_a_1, VFF_1)
    frame_array_a_2 = sm.edit_volume_by_factor(frame_array_a_2, VFF_2)

    # cut bass from last bar from Song A for smoother transition
    frame_array_a_2 = sm.cut_bass_for_last_bar(frame_array_a_2, TSL_1/2)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b)//2]
    frame_array_b_2 = frame_array_b[len(frame_array_b)//2:]

    # slowly increase volume of Song B & remove Bass
    frame_array_b_1 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_b_1, VFF_4), order=3)
    frame_array_b_2 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_b_2, VFF_3), order=3)

    # merge both pieces again
    transition_song_a = np.append(frame_array_a_1, frame_array_a_2)
    transition_song_b = np.append(frame_array_b_1, frame_array_b_2)

    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# Song B with full Bass
def modify_transition_segment_2(frame_array_a, frame_array_b):

    # --- modifying Song A ---
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a)//2]
    frame_array_a_2 = frame_array_a[len(frame_array_a)//2:]

    # slowly decrease volume of Song A & remove Bass
    frame_array_a_1 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_a_1, VFF_3), order=3)
    frame_array_a_2 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_a_2, VFF_4), order=3)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b)//2]
    frame_array_b_2 = frame_array_b[len(frame_array_b)//2:]

    # slowly increase volume of Song B
    frame_array_b_1 = sm.edit_volume_by_factor(frame_array_b_1, VFF_2)
    frame_array_b_2 = sm.edit_volume_by_factor(frame_array_b_2, VFF_1)

    # cut bass from last bar from Song B for smoother transition
    frame_array_b_2 = sm.cut_bass_for_last_bar(frame_array_b_2, TSL_2/2)

    # merge both pieces again
    transition_song_a = np.append(frame_array_a_1, frame_array_a_2)
    transition_song_b = np.append(frame_array_b_1, frame_array_b_2)

    combined_songs = []
    for i in range(len(transition_song_a)):
        combined_songs.append(transition_song_a[i] + transition_song_b[i])

    return np.array(combined_songs)


# this method will combine the frames of song a & b in two separate time segments (C -- D & D -- E)
def mix_transition_segments(song_a, song_b, transition_points, frames):
    segment_channels_a = [[], []]
    segment_channels_b = [[], []]

    print("INFO -   Calculating Transition Segment: C -- D, Length in bars: '%s'" % TSL_1)
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

    print("INFO -   Calculating Transition Segment: D -- E, Length in bars: '%s'" % TSL_2)
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


def create_mixed_wav_file(song_a, song_b, transition_points, paths, frames):
    log_info_about_mix(song_a, song_b, transition_points, frames)
    print("INFO - Keep calm... Mixing both audiofiles.")

    if not song_a['frame_rate'] == 44100 and not song_b['frame_rate'] == 44100:
        print("ERROR - Skipping mixing because sample rate is not 44.100Hz for both songs.")
        sys.exit()

    print("INFO - Adding unmodified frames of song A to mix. Length: '%0.2f's" % transition_points['c'])
    # reading song a just until point C and get all frames for both channels
    song_x = librosa.core.load(song_a['path'], sr=SAMPLE_RATE, mono=False, duration=transition_points['c'])
    left_mix_channel = song_x[0][0]
    right_mix_channel = song_x[0][1]

    print("INFO - Creating transition segments between A & B. Length: '%0.2f's" % (
                transition_points['e'] - transition_points['c']))
    transition_segment_left, transition_segment_right = mix_transition_segments(song_a, song_b, transition_points, frames)
    left_mix_channel = np.append(left_mix_channel, transition_segment_left)
    right_mix_channel = np.append(right_mix_channel, transition_segment_right)
    del transition_segment_left, transition_segment_right

    print("INFO - Adding unmodified frames of song B to mix. Length: '%0.2f's" % (
            song_b['total_frames'] / SAMPLE_RATE - transition_points['x']))
    transition_time = transition_points['e'] - transition_points['c']
    start_of_b = int(round((transition_points['a'] + transition_time) * SAMPLE_RATE))
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
        len(left_mix_channel), get_length_out_of_frames(len(left_mix_channel))))
    return np.array([left_mix_channel, right_mix_channel], dtype='float32', order='F')


if __name__ == '__main__':
    #	--- vibrancy to brethren --- C-D-E: 4,48-6,18-6,48 --- 48-16
    transition_points = {
        'a': 0.128,
        'c': 240 + 48 + 0.875,
        'd': 360 + 18 + 0.875,
        'e': 360 + 48 + 0.875
    }
    transition_points['b'] = transition_points['a'] + (transition_points['d'] - transition_points['c'])
    transition_points['x'] = transition_points['a'] + (transition_points['e'] - transition_points['c'])
    paths = {'song_a_path': "../AudioExampleFiles/Umek - Vibrancy (Original Mix).wav",
             'song_b_path': "../AudioExampleFiles/Umek - Brethren (Original Mix).wav",
             'result_path': "../AudioExampleFiles/Mixes/" + "vibrancy_to_brethren_" + str(transition_points['a']) + ".wav"
             }

    song_a = read_wav_file(paths['song_a_path'])
    song_b = read_wav_file(paths['song_b_path'])
    frames = calculate_frames(song_a, song_b, transition_points)

    print("Frames: %s" % frames)
    print("Transition Points: %s" % transition_points)

    then = time.time()
    mixed_song = create_mixed_wav_file(song_a, song_b, transition_points, paths, frames)
    save_wav_file(mixed_song, paths['result_path'])
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now-then))



