import librosa
import numpy
from . import utility as util


def match_bpm_first(config, song_a, tempo_a, song_b, tempo_b):

    # signal_b, rate_b = librosa.load(f"{config['song_path']}/{song_b['name']}")
    #
    # tempo_b, beats_b = librosa.beat.beat_track(y=signal_b.T, sr=rate_b)

    rate_b = song_b['frame_rate']

    tempo_ratio = tempo_a / tempo_b
    new_rate_b = rate_b / tempo_ratio

    print("INFO - Matching tempo of song "+song_b['name']+" ("+str(tempo_b)+") to tempo of song "+song_a.name+" ("+str(tempo_a)+")")
    song_b_0_resampled = librosa.resample(song_b['left_channel'], rate_b, new_rate_b)
    song_b_1_resampled = librosa.resample(song_b['right_channel'], rate_b, new_rate_b)


    song_b_resampled = numpy.array([song_b_0_resampled, song_b_1_resampled])

    song_b_name_split = song_b['name'].split('.')
    stretch_path_b = f"{config['data_path']}/{song_b_name_split[0]}_adjusted.wav"

    librosa.output.write_wav(stretch_path_b, song_b_resampled, rate_b)

    song_b = util.read_wav_file(config, stretch_path, identifier='songB')

    # song_b['frames'] = song_b_resampled[0]
    # song_b['left_channel'] = song_b_resampled[0][0]
    # song_b['right_channel'] = song_b_resampled[0][1]

    return song_a, song_b

def match_bpm_desired(config, song_a, tempo_a, song_b, tempo_b, desired_tempo):

    # signal_a, rate_a = librosa.load(f"{config['song_path']}/{song_a['name']}")
    # signal_b, rate_b = librosa.load(f"{config['song_path']}/{song_b['name']}")
    #
    # tempo_a, beats_a = librosa.beat.beat_track(y=signal_a.T, sr=rate_a)
    # tempo_b, beats_b = librosa.beat.beat_track(y=signal_b.T, sr=rate_b)

    rate_a = song_a['frame_rate']
    rate_b = song_b['frame_rate']

    tempo_ratio_a = desired_tempo / tempo_a
    new_rate_a = rate_a / tempo_ratio_a

    print("INFO - Matching tempos of song "+song_a['name']+" ("+str(tempo_a)+") to desired tempo "+str(desired_tempo))
    song_a_0_resampled = librosa.resample(song_a['left_channel'], rate_a, new_rate_a)
    song_a_1_resampled = librosa.resample(song_a['right_channel'], rate_b, new_rate_a)


    song_a_resampled = numpy.array([song_a_0_resampled, song_a_1_resampled])

    song_a_name_split = song_a['name'].split('.')
    stretch_path_a = f"{config['data_path']}/{song_a_name_split[0]}_adjusted.wav"

    librosa.output.write_wav(stretch_path_a, song_a_resampled, rate_a)

    song_a = util.read_wav_file(config, stretch_path_a, identifier='songB')

    # song_a['frames'] = song_a_resampled[0]
    # song_a['left_channel'] = song_a_resampled[0][0]
    # song_a['right_channel'] = song_a_resampled[0][1]

    tempo_ratio_b = desired_tempo / tempo_b
    new_rate_b = rate_b / tempo_ratio_b

    print("INFO - Matching tempos of song "+song_b['name']+" ("+str(tempo_b)+") to desired tempo "+str(desired_tempo))
    song_b_0_resampled = librosa.resample(song_b['left_channel'], rate_b, new_rate_b)
    song_b_1_resampled = librosa.resample(song_b['right_channel'], rate_b, new_rate_b)


    song_b_resampled = numpy.array([song_b_0_resampled, song_b_1_resampled])

    song_b_name_split = song_b['name'].split('.')
    stretch_path_b = f"{config['data_path']}/{song_b_name_split[0]}_adjusted.wav"

    librosa.output.write_wav(stretch_path_b, song_b_resampled, rate_b)

    song_b = util.read_wav_file(config, stretch_path_b, identifier='songB')

    # song_b['frames'] = song_b_resampled[0]
    # song_b['left_channel'] = song_b_resampled[0][0]
    # song_b['right_channel'] = song_b_resampled[0][1]

    return song_a, song_b
