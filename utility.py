#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# wav files will be read & written with the librosa module

import librosa

SAMPLE_RATE = 44100


def read_wav_file(filepath, duration=None):
    # alternatives: soundfile, wav, sciPy, pydub
    # oder pydub nutzen? https://stackoverflow.com/questions/37999150/python-how-to-split-a-wav-file-into-multiple-wav-files/43367691
    print("INFO - Reading song '%s'" % filepath)

    librosa_load = librosa.core.load(filepath, sr=SAMPLE_RATE, mono=False, duration=duration)
    song = {'frames': librosa_load[0],
            'left_channel': librosa_load[0][0],
            'right_channel': librosa_load[0][1],
            'frame_rate': librosa_load[1],
            'path': filepath,
            'name': filepath.split('/')[len(filepath.split('/')) - 1]
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
