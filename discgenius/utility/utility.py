#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this script will provide some useful methods like reading & saving files
# wav files will be read & written with the librosa module

import json
import os
from os.path import isfile, join

import librosa


def read_wav_file(config, filepath, duration=None, identifier=None):
    # alternatives: soundfile, wav, sciPy, pydub
    print("INFO - Reading song '%s'" % filepath)

    librosa_load = librosa.core.load(filepath, sr=config['sample_rate'], mono=False, duration=duration)
    song = {'frames': librosa_load[0],
            'left_channel': librosa_load[0][0],
            'right_channel': librosa_load[0][1],
            'frame_rate': librosa_load[1],
            'path': filepath,
            'name': filepath.split('/')[len(filepath.split('/')) - 1]
            }
    if identifier:
        song['identifier'] = identifier
    song['total_frames'] = len(song['frames'][0])
    song['length'] = get_length_out_of_frames(config, song['total_frames'])

    print("INFO - Parameters: Framerate '%s', Total Frames '%s', Length '%sm'\n" % (
        song['frame_rate'], song['total_frames'], song['length']))
    return song


def save_wav_file(config, list_of_frames, path):
    i = 1
    while os.path.exists(path):
        path = f"{path[:-4]}-{i}.wav"
        i += 1

    print("INFO - Saving mixed audio file to '%s'" % path)
    librosa.output.write_wav(path, list_of_frames, config['sample_rate'], norm=True)
    print("SUCCESS - Finished saving.")
    # sf.write(path, list_of_frames, samplerate, subtype='FLOAT', format='WAV')
    # scipy.io.wavfile.write(path, samplerate, list_of_frames)

    return path


def move_audio_to_storage(config, filepath):
    print("------------------------------------------------------------------------------------------------------------------------")
    print(filepath)
    print(config['mp3_storage'])
    audio_file = filepath.split('/')[-1]
    print(audio_file)
    os.rename(filepath, f"{config['mp3_storage']}/{audio_file}")


def get_length_out_of_frames(config, amount_of_frames):
    length_in_seconds = amount_of_frames / config['sample_rate']
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


def calculate_frames(config, song_a, song_b, transition_points):
    sample_rate = config['sample_rate']
    frames = {
        'complete_song_a': song_a['total_frames'],
        'complete_song_b': song_b['total_frames'],
        'until_a': int(round(transition_points['a'] * sample_rate)),
        'until_b': int(round(transition_points['b'] * sample_rate)),
        'until_x': int(round(transition_points['x'] * sample_rate)),
        'until_c': int(round(transition_points['c'] * sample_rate)),
        'until_d': int(round(transition_points['d'] * sample_rate)),
        'until_e': int(round(transition_points['e'] * sample_rate)),
        'between_c_and_d': int(round((transition_points['d'] - transition_points['c']) * sample_rate)),
        'between_d_and_e': int(round((transition_points['e'] - transition_points['d']) * sample_rate))
    }
    return frames


def get_scenario(config, scenario_name):
    for f in os.listdir(config['scenario_path']):
        if f == f"{scenario_name}.json":
            path = join(config['scenario_path'], f)
            with open(path) as json_file:
                return json.load(json_file)


def get_scenarios(config, just_names=True):
    scenarios = []
    for f in os.listdir(config['scenario_path']):
        path = join(config['scenario_path'], f)
        if isfile(path) and '.json' in f:
            with open(path) as json_file:
                if just_names:
                    scenarios.append(f[:-5])
                else:
                    scenarios.append({f[:-5]: json.load(json_file)})
    return scenarios


def export_transition_parameters_to_json(config, list_of_songs, transition_points, scenario_data, tsl_list):
    print("INFO - Generating json-file that stores transition process.")
    mix_name = ""
    json_data = {}
    for song in list_of_songs:
        json_data[song['identifier']] = song
        if song['identifier'] == "mix":
            mix_name = song['name']
        for key in config['keys_to_remove']:
            if key in song:
                del song[key]

    json_data['scenario'] = scenario_data
    json_data['transitions'] = {}

    # transition segment 1
    transition_segment = {
        'length_in_bars': tsl_list[0],
        'length_in_seconds': round(transition_points['d'] - transition_points['c'], 3),
        'transition_points_in_seconds': {
            'start_at_A': transition_points['c'],
            'end_at_A': transition_points['d'],
            'start_at_B': transition_points['a'],
            'end_at_B': transition_points['b'],
        }}
    # parameters = transition_scenario['fading_parameters']
    # transition_segment['EQ_values_A'] = {
    #    'highs': parameters[:len(transition_scenario['fading_parameters']) // 2],
    #    'mids': parameters[:len(transition_scenario['fading_parameters']) // 2],
    #    'lows': [0, 0, 0, 0]
    # }
    # transition_segment['EQ_values_B'] = {
    #    'highs': parameters[len(transition_scenario['fading_parameters']) // 2:],
    #    'mids': parameters[len(transition_scenario['fading_parameters']) // 2:],
    #    'lows': [-32, -32, -32, -32]
    # }
    json_data['transitions']['segment_1'] = transition_segment

    # transition segment 2
    transition_segment = {'length_in_bars': tsl_list[1],
                          'length_in_seconds': round(transition_points['e'] - transition_points['d'], 3),
                          'transition_points_in_seconds': {
                              'start_at_A': transition_points['d'],
                              'end_at_A': transition_points['e'],
                              'start_at_B': transition_points['b'],
                              'end_at_B': transition_points['x'],
                          }}
    # parameters = transition_scenario['fading_parameters']
    # transition_segment['EQ_values_A'] = {
    #    'highs': parameters[len(transition_scenario['fading_parameters']) // 2:],
    #    'mids': parameters[len(transition_scenario['fading_parameters']) // 2:],
    #    'lows': [-32, -32, -32, -32]
    # }
    # transition_segment['EQ_values_B'] = {
    #    'highs': parameters[:len(transition_scenario['fading_parameters']) // 2],
    #    'mids': parameters[:len(transition_scenario['fading_parameters']) // 2],
    #    'lows': [0, 0, 0, 0]
    # }
    json_data['transitions']['segment_2'] = transition_segment

    save_path = f"{config['data_path']}/data_{mix_name}.json"
    with open(save_path, 'w') as fp:
        pretty_json = json.dumps(json_data, indent=2)
        fp.write(pretty_json)
    return json_data
