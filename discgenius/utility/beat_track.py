from os import path
import json

from .sound_manipulation import high_cut_filter
from .utility import read_wav_file, save_wav_file

import numpy
import aubio
import librosa


def aubio_beats_to_bpm(beats):
    # if enough beats are found, convert to periods then to bpm
    if len(beats) > 1:
        if len(beats) < 4:
            print("few beats found.")
        bpms = 60./numpy.diff(beats)
        return numpy.median(bpms)
    else:
        print("not enough beats found")
        return 0


def aubio_beat_tracking(filepath, sample_rate, win_s=512):
    win_s = win_s               # fft size
    hop_s = win_s // 2          # hop size
    src = aubio.source(filepath, hop_size=hop_s)
    #print(f"file: {src.uri}, samplerate: {src.samplerate}, channels: {src.channels}, duration: {src.duration/src.samplerate}")

    o = aubio.tempo("default", win_s, hop_s, sample_rate)

    # tempo detection delay, in samples
    # default to 4 blocks delay to catch up with
    delay = 4. * hop_s

    # list of beats, in samples
    beats = []

    # total number of frames read
    total_frames = 0
    while True:
        samples, read = src()
        is_beat = o(samples)
        if is_beat:
            this_beat = int(total_frames - delay + is_beat[0] * hop_s)
            #print("%f" % (this_beat / float(SAMPLE_RATE)))
            beats.append(this_beat/sample_rate)
        total_frames += read
        if read < hop_s: break

    bpm = aubio_beats_to_bpm(beats)
    print(f"INFO - Analysis: Aubio beat detection finished. BPM of song: {bpm}, amount of beats found: {len(beats)}")
    return beats, bpm


def aubio_beat_track_with_lpf_before(config, filepath, sample_rate, win_s=512, freq=250):
    song = read_wav_file(config, filepath=filepath, debug_info=False)

    # modify signal with low pass filter
    left_channel = high_cut_filter(song['left_channel'], order=3, freq=freq)
    right_channel = high_cut_filter(song['right_channel'], order=3, freq=freq)

    new_filepath = f"{config['song_path']}/audio_highs_cutted.wav"
    save_wav_file(config, numpy.array([left_channel, right_channel], dtype='float32', order='F'), new_filepath, debug_info=False)
    return aubio_beat_tracking(new_filepath, sample_rate, win_s=win_s)


# time intensive beat frame detection using librosa.
# TODO needs to be run less per analysis to improve performance.
def librosa_beat_tracking(config, signal, song, entry_point):
    sample_rate = song['frame_rate']

    # create signal partition based on given entry point
    entry_point_index = round(len(signal) * entry_point)
    if entry_point > 0.5:
        signal_part = signal[entry_point_index:]
    else:
        signal_part = signal[:entry_point_index]

    # check if beat tracking was done already and take saved status
    beat_tracking_path = f"{config['song_analysis_path']}/{song['name']}_{song['bpm']}.json"
    if path.exists(beat_tracking_path):
        tempo, beats = get_beat_tracking_from_file(beat_tracking_path)
        print(f"\t\t Read tempo & beats from file. BPM of song: {tempo}, amount of beats found: {len(beats)}")
    else:
        # compute onset envelopes
        onset_env = librosa.onset.onset_strength(y=signal_part, sr=sample_rate, aggregate=numpy.median)

        # compute beats using librosa beat tracking
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sample_rate)

        # save beat tracking
        save_beat_tracking_to_file(beat_tracking_path, tempo, beats)

        print(f"\t\t Librosa beat detection finished. BPM of song: {tempo}, amount of beats found: {len(beats)}")

    # create onset sample matrix from tracked beats
    onset_samples = list(librosa.frames_to_samples(beats))
    onset_samples = numpy.concatenate(onset_samples, len(signal_part))

    # derive frame index of beat starts/stops from onset sample matrix
    starts = onset_samples[0:-1]
    stops = onset_samples[1:]

    times_starts = librosa.samples_to_time(starts, sr=sample_rate)
    times_stops = librosa.samples_to_time(stops, sr=sample_rate)

    # offset times values based on entry_point if we aim to find exit segments
    if entry_point > 0.5:
        times_offset = (len(signal)/sample_rate)*entry_point
        times_starts = [t + times_offset for t in times_starts]
        times_stops = [t + times_offset for t in times_stops]

    return times_starts, times_stops


def librosa_beat_tracking_with_mono_signal(config, song, entry_point):
    song = read_wav_file(config, filepath=song['path'], debug_info=False)
    return librosa_beat_tracking(config, song['mono'], song, entry_point)


def get_beat_tracking_from_file(beat_path):
    with open(beat_path, mode='r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data['bpm'], json_data['beats']


def save_beat_tracking_to_file(beat_path, tempo, beats):
    song_analysis = {
        'bpm': tempo,
        'beats': numpy.ndarray.tolist(beats)
    }
    with open(beat_path, mode='w', encoding='utf-8') as file:
        json.dump(song_analysis, file, indent=2)
    return True
