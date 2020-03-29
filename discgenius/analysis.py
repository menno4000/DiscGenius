import librosa
import librosa.display
import numpy

from .utility import segment_scorer as scorer
from .utility import beat_track

hop_length = 512
clip_size = 4 # amount of beats that a clips size will be. these clips will be compared. reasonable values: 1, 4, 8
step_size = 1 # the smaller the better outcome, but higher load

transition_points = {}


def segment_song(config, signal, times_of_beats, clip_size, step_size, transition_length, transition_midpoint):
    clips = []
    areas = {}
    sample_rate = config['sample_rate']
    amount_of_areas = len(times_of_beats) - transition_length

    for i in range(0, len(times_of_beats)-clip_size):
        # create possible areas for transition
        if i < amount_of_areas and i%step_size == 0:
            begin_of_segment = times_of_beats[i]
            midpoint = times_of_beats[i + transition_midpoint]
            end_of_segment = times_of_beats[i + transition_length]
            areas[i] = [begin_of_segment, midpoint, end_of_segment]

        # create clip
        start = int(times_of_beats[i] * sample_rate)
        stop = int(times_of_beats[i + clip_size] * sample_rate)
        clip = signal[start:stop]
        clips.append(clip)
    return areas, clips


# calculates transition points dictionary for a transition of given between two given songs
def get_transition_points(config, song_a, song_b, transition_length, transition_midpoint):
    mono_signal_a = song_a['mono']
    mono_signal_b = song_b['mono']

    print("INFO - Analysis: Beat detection for both songs.")

    # aubio
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_tracking(song_a['path'], sample_rate)
    #times_of_beats_b, bpm_b = beat_track.aubio_beat_tracking(song_b['path'], sample_rate)

    # aubio with lpf before
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_track_with_lpf_before(config, song_a['path'], sample_rate)
    #times_of_beats_b, bpm_b = beat_track.aubio_beat_track_with_lpf_before(config, song_b['path'], sample_rate)

    # librosa with start times
    #times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking(signal_a, sample_rate)
    #times_of_beats_b, stop_times_of_beats_b = beat_track.librosa_beat_tracking(signal_b, sample_rate)

    # librosa with mono signal input --> best results
    times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking_with_mono_signal(config, song_a)
    times_of_beats_b, stop_times_of_beats_b = beat_track.librosa_beat_tracking_with_mono_signal(config, song_b)


    # split song into clip segments of even number of consecutive beats
    print("INFO - Analysis: Creating segments for comparison.")
    areas_a, clips_a = segment_song(config, mono_signal_a, times_of_beats_a, clip_size, step_size, transition_length, transition_midpoint)
    areas_b, clips_b = segment_song(config, mono_signal_b, times_of_beats_b, clip_size, step_size, transition_length, transition_midpoint)

    print("INFO - Analysis: Finding best segments.")
    # score segments using segment_scorer utility class
    segment_scores_a = scorer.score_segments(config, clips_a, areas_a, transition_length, transition_midpoint, clip_size, step_size, bias_mode=False)
    segment_scores_b = scorer.score_segments(config, clips_b, areas_b, transition_length, transition_midpoint, clip_size, step_size, bias_mode=True)

    #print(f"segment scores: length of 1: {len(segment_scores_a)}, 2: {len(segment_scores_b)}")

    # determine best transition candidates
    #best_segment_index_a = segment_scores_a.index(min(segment_scores_a))
    #best_segment_index_b = segment_scores_b.index(min(segment_scores_b))
    best_segment_index_a = min(segment_scores_a, key=segment_scores_a.get)
    best_segment_index_b = min(segment_scores_b, key=segment_scores_b.get)

    print(f"Selected indexes for songs A: {best_segment_index_a}, B: {best_segment_index_b}")
    #print(segment_times1)

    print("INFO - Analysis: Generating transition points.")
    transition_points['c'] = areas_a[best_segment_index_a][0]
    transition_points['d'] = areas_a[best_segment_index_a][1]
    transition_points['e'] = areas_a[best_segment_index_a][2]

    transition_points['a'] = areas_b[best_segment_index_b][0]
    transition_points['b'] = areas_b[best_segment_index_b][1]
    transition_points['x'] = areas_b[best_segment_index_b][2]

    return transition_points
