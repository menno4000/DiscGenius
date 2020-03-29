import librosa
import numpy

from . import utility as util


def adjust_tempo(config, song_name, song_tempo, song_tempo_new):
    song = librosa.core.load(f"{config['song_path']}/{song_name}")
    new_song_name = song_name.split('_')[0] + '_' + str(song_tempo_new)
    stretch_path = f"{config['song_path']}/{new_song_name}.wav"
    rate = song[1]

    tempo_ratio = song_tempo_new / song_tempo
    new_rate = (rate / tempo_ratio)

    print(
        "INFO - Creating adjusted tempo copy of song " + song_name + " (" + str(song_tempo) + ") with new tempo " + str(
            song_tempo_new))
    song_resampled_0 = librosa.resample(song[0][0], rate, new_rate)
    song_resampled_1 = librosa.resample(song[0][1], rate, new_rate)

    song_resampled = numpy.array([song_resampled_0, song_resampled_1])

    librosa.output.write_wav(stretch_path, song_resampled, rate)
    print("INFO - Created adjusted tempo compy of song " + song_name + ".")

    return new_song_name


def match_bpm_first(config, song_a, tempo_a, song_b, tempo_b):
    if tempo_a == tempo_b:
        return song_a, song_b

    rate_b = song_b['frame_rate']
    song_b_name_split = song_b['name'].split('.')
    stretch_path_b = f"{config['song_path']}/{song_b_name_split[0]}_adjusted.wav"

    # song a remains at same tempo, song b is resampled to bpm of song A
    tempo_ratio = tempo_a / tempo_b
    new_rate_b = rate_b / tempo_ratio

    print("INFO - Matching tempo of song " + song_b['name'] + " (" + str(tempo_b) + ") to tempo of song " + song_a[
        'name'] + " (" + str(tempo_a) + ")")
    song_b_0_resampled = librosa.resample(song_b['left_channel'], rate_b, new_rate_b)
    song_b_1_resampled = librosa.resample(song_b['right_channel'], rate_b, new_rate_b)

    song_b_resampled = numpy.array([song_b_0_resampled, song_b_1_resampled])

    librosa.output.write_wav(stretch_path_b, song_b_resampled, rate_b)
    song_b_adjusted = util.read_wav_file(config, stretch_path_b, identifier='songB')

    return song_a, song_b_adjusted


def match_bpm_desired(config, song_a, tempo_a, song_b, tempo_b, desired_tempo):
    song_a_name_split = song_a['name'].split('.')
    song_b_name_split = song_b['name'].split('.')

    stretch_path_a = f"{config['data_path']}/{song_a_name_split[0]}_adjusted.wav"
    stretch_path_b = f"{config['data_path']}/{song_b_name_split[0]}_adjusted.wav"

    rate_a = song_a['frame_rate']
    rate_b = song_b['frame_rate']

    if round(tempo_a, 3) != desired_tempo:
        tempo_ratio_a = desired_tempo / tempo_a
        new_rate_a = rate_a / tempo_ratio_a

        print("INFO - Matching tempos of song " + song_a['name'] + " (" + str(tempo_a) + ") to desired tempo " + str(
            desired_tempo))
        song_a_0_resampled = librosa.resample(song_a['left_channel'], rate_a, new_rate_a)
        song_a_1_resampled = librosa.resample(song_a['right_channel'], rate_a, new_rate_a)

        song_a_resampled = numpy.array([song_a_0_resampled, song_a_1_resampled])

        librosa.output.write_wav(stretch_path_a, song_a_resampled, rate_a)
        song_a_adjusted = util.read_wav_file(config, stretch_path_a, identifier='songA')

    else:
        librosa.output.write_wav(stretch_path_a, song_a['frames'], rate_a)
        song_a_adjusted = util.read_wav_file(config, stretch_path_a, identifier='songA')

    if round(tempo_b, 3) != desired_tempo:
        tempo_ratio_b = desired_tempo / tempo_b
        new_rate_b = rate_b / tempo_ratio_b

        print("INFO - Matching tempos of song " + song_b['name'] + " (" + str(tempo_b) + ") to desired tempo " + str(
            desired_tempo))
        song_b_0_resampled = librosa.resample(song_b['left_channel'], rate_b, new_rate_b)
        song_b_1_resampled = librosa.resample(song_b['right_channel'], rate_b, new_rate_b)

        song_b_resampled = numpy.array([song_b_0_resampled, song_b_1_resampled])

        librosa.output.write_wav(stretch_path_b, song_b_resampled, rate_b)

        song_b_adjusted = util.read_wav_file(config, stretch_path_b, identifier='songB')
    else:
        librosa.output.write_wav(stretch_path_b, song_b['frames'], rate_b)
        song_b_adjusted = util.read_wav_file(config, stretch_path_b, identifier='songB')

    return song_a_adjusted, song_b_adjusted
