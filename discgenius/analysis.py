import librosa
import librosa.display
import numpy

from .utility import segment_scorer as scorer
from .utility import aubio

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

    print("INFO - Analysis: beat detection for both songs")


    aubio_beats_a, bpm_a = aubio.aubio_beat_tracking(song_a['path'], sample_rate)
    aubio_beats_b, bpm_b = aubio.aubio_beat_tracking(song_b['path'], sample_rate)

    # split song into clip segments of even number of consecutive beats
    clips_a = []
    clips_b = []

    segment_times1 = {}
    segment_times2 = {}

    print("INFO - Analysis: Finding transition points.")
    for i in range(0, (len(aubio_beats_a) - (transition_length * clip_size)), 1):
        start = int(aubio_beats_a[i]*sample_rate)
        stop = int(aubio_beats_a[i + clip_size]*sample_rate)
        #print(start, stop)
        clip = signal_a[start:stop]
        clips_a.append(clip)
        segment_times1[i] = [(aubio_beats_a[i]), (aubio_beats_a[i + (transition_midpoint * int(clip_size / 2))]),
                             (aubio_beats_a[i + (transition_midpoint * clip_size)])]

    for i in range(0, (len(aubio_beats_b) - (transition_length * clip_size)), 1):
        start = int(aubio_beats_b[i]*sample_rate)
        stop = int(aubio_beats_b[i + clip_size]*sample_rate)
        clip = signal_b[start:stop]
        clips_b.append(clip)
        segment_times2[i] = [(aubio_beats_b[i]), (aubio_beats_b[i + (transition_midpoint * int(clip_size / 2))]),
                             (aubio_beats_b[i + (transition_midpoint * clip_size)])]


    # score segments using segment_scorer utility class
    segment_scores1 = scorer.score_segments(clips_a, transition_length, transition_midpoint, False)
    segment_scores2 = scorer.score_segments(clips_b, transition_length, transition_midpoint, True)

    # determine best transition candidates
    best_segment_index1 = segment_scores1.index(min(segment_scores1))
    best_segment_index2 = segment_scores2.index(min(segment_scores2))

    transition_points['c'] = segment_times1[best_segment_index1][0]
    transition_points['d'] = segment_times1[best_segment_index1][1]
    transition_points['e'] = segment_times1[best_segment_index1][2]

    transition_points['a'] = segment_times2[best_segment_index2][0]
    transition_points['b'] = segment_times2[best_segment_index2][1]
    transition_points['x'] = segment_times2[best_segment_index2][2]

    return transition_points
