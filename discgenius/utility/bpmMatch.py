from os import path

import librosa
from scipy import signal
import aubio
import numpy

from . import utility as util


def scipy_resample(frame_array, ratio):
    amount_of_frames = int(len(frame_array) * ratio)
    return signal.resample(frame_array, amount_of_frames)


def adjust_tempo(config, song_name, bpm, desired_bpm, song=None):
    if not song:
        song = util.read_wav_file(config, f"{config['song_path']}/{song_name}_{bpm}.wav")

    new_song_name = f"{song_name}_{str(desired_bpm)}.wav"
    new_filepath = f"{config['song_path']}/{new_song_name}"

    # if song with bpm exists, use existing
    if path.exists(new_filepath):
        #print(f"SKIP - Song '{new_filepath}' already exists.")
        return new_song_name

    sample_rate = song['frame_rate']
    tempo_ratio = desired_bpm / bpm
    new_rate = sample_rate / tempo_ratio

    #song_0_resampled = scipy_resample(song['left_channel'], bpm/desired_bpm)
    #song_1_resampled = scipy_resample(song['right_channel'], bpm/desired_bpm)

    song_0_resampled = librosa.resample(song['left_channel'], sample_rate, new_rate)
    song_1_resampled = librosa.resample(song['right_channel'], sample_rate, new_rate)

    song_resampled = numpy.asfortranarray([song_0_resampled, song_1_resampled])

    librosa.output.write_wav(new_filepath, song_resampled, sample_rate)
    print(f"INFO - Saved adjusted song to '{new_filepath}'")
    return new_song_name


def match_bpm_first(config, song_a, tempo_a, song_b, tempo_b):
    if tempo_a == tempo_b:
        return song_a, song_b

    print(f"INFO - Matching song B ({tempo_b}) to tempo of song A ({tempo_a}).")
    adjusted_song_b_name = adjust_tempo(config, song_b['name'], tempo_b, tempo_a, song=song_b)
    song_b_adjusted = util.read_wav_file(config, f"{config['song_path']}/{adjusted_song_b_name}", debug_info=False, identifier='songB')

    return song_a, song_b_adjusted


def match_bpm_desired(config, song_a, song_b, desired_bpm, bpm_a, bpm_b):
    if bpm_a == bpm_b and bpm_a == desired_bpm:
        return song_a, song_b

    print(f"INFO - Matching song A ({bpm_a}) & B ({bpm_b}) to desired tempo ({desired_bpm}).")
    adjusted_song_a_name = adjust_tempo(config, song_a['name'], bpm_a, desired_bpm, song=song_a)
    adjusted_song_b_name = adjust_tempo(config, song_b['name'], bpm_b, desired_bpm, song=song_b)

    song_a_adjusted = util.read_wav_file(config, f"{config['song_path']}/{adjusted_song_a_name}", debug_info=False, identifier='songA')
    song_b_adjusted = util.read_wav_file(config, f"{config['song_path']}/{adjusted_song_b_name}", debug_info=False, identifier='songB')
    return song_a_adjusted, song_b_adjusted
