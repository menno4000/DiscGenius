import librosa
import librosa.display
import numpy

from .utility import segment_scorer as scorer
from .utility import beat_track

hop_length = 512
clip_size = 8

transition_points = {}


# calculates transition points dictionary for a transition of given between two given songs
def get_transition_points(config, song_a, song_b, transition_length, transition_midpoint):
    print(f"INFO - Transition length: {transition_length}, transition midpoint: {transition_midpoint}")

    signal_a = song_a['left_channel']
    sample_rate = song_a['frame_rate']

    signal_b = song_b['left_channel']
    # signal2, rate2 = librosa.load(f"{config['data_path']}/{song_b['name']}", sr=config['sample_rate'])

    print("INFO - Analysis: Beat detection for both songs.")

    # aubio
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_tracking(song_a['path'], sample_rate)
    #times_of_beats_b, bpm_b = beat_track.aubio_beat_tracking(song_b['path'], sample_rate)

    # aubio with lpf before
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_track_with_lpf_before(config, song_a['path'], sample_rate)
    #times_of_beats_b, bpm_b = beat_track.aubio_beat_track_with_lpf_before(config, song_b['path'], sample_rate)

    #print()
    #print(times_of_beats_a[50:100])
    #print(lpf_beats[50:100])

    # librosa with start times
    #times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking(signal_a, sample_rate)
    #times_of_beats_b, stop_times_of_beats_b = beat_track.librosa_beat_tracking(signal_b, sample_rate)

    # librosa with mono signal input
    times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking_with_mono_signal(config, song_a)
    times_of_beats_b, stop_times_of_beats_b = beat_track.librosa_beat_tracking_with_mono_signal(config, song_b)


    # split song into clip segments of even number of consecutive beats
    clips_a = []
    clips_b = []

    segment_times1 = {}
    segment_times2 = {}

    print("INFO - Analysis: Creating segments for comparison.")
    for i in range(0, (len(times_of_beats_a) - (transition_length * clip_size)), 1):
        start = int(times_of_beats_a[i]*sample_rate)
        stop = int(times_of_beats_a[i + clip_size]*sample_rate)
        #print(start, stop)
        clip = signal_a[start:stop]
        clips_a.append(clip)
        segment_times1[i] = [(times_of_beats_a[i]), (times_of_beats_a[i + (transition_midpoint * int(clip_size / 2))]),
                             (times_of_beats_a[i + (transition_midpoint * clip_size)])]

    for i in range(0, (len(times_of_beats_b) - (transition_length * clip_size)), 1):
        start = int(times_of_beats_b[i]*sample_rate)
        stop = int(times_of_beats_b[i + clip_size]*sample_rate)
        clip = signal_b[start:stop]
        clips_b.append(clip)
        segment_times2[i] = [(times_of_beats_b[i]), (times_of_beats_b[i + (transition_midpoint * int(clip_size / 2))]),
                             (times_of_beats_b[i + (transition_midpoint * clip_size)])]

    print("INFO - Analysis: Finding best segments.")
    # score segments using segment_scorer utility class
    segment_scores1 = scorer.score_segments(clips_a, transition_length, transition_midpoint, False)
    segment_scores2 = scorer.score_segments(clips_b, transition_length, transition_midpoint, True)

    # determine best transition candidates
    best_segment_index1 = segment_scores1.index(min(segment_scores1))
    best_segment_index2 = segment_scores2.index(min(segment_scores2))

    print("INFO - Analysis: Generating transition points.")
    transition_points['c'] = segment_times1[best_segment_index1][0]
    transition_points['d'] = segment_times1[best_segment_index1][1]
    transition_points['e'] = segment_times1[best_segment_index1][2]

    transition_points['a'] = segment_times2[best_segment_index2][0]
    transition_points['b'] = segment_times2[best_segment_index2][1]
    transition_points['x'] = segment_times2[best_segment_index2][2]

    return transition_points
