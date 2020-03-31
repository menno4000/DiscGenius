from .utility import beat_track
from .utility import segment_scorer as scorer

hop_length = 512

transition_points = {}


def segment_song(config, signal, times_of_beats):
    clips = []
    areas = {}
    clip_size = config['clip_size']
    step_size = config['step_size']
    transition_length = config['transition_length']
    transition_midpoint = config['transition_midpoint']
    sample_rate = config['sample_rate']
    amount_of_areas = len(times_of_beats) - transition_length - clip_size

    for i in range(0, len(times_of_beats) - clip_size):
        # create possible areas for transition
        if i < amount_of_areas and i % step_size == 0:
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
def find_best_segments(config, song, bias_mode):
    mono_signal = song['mono']

    print(f"INFO - Analysis: Beat detection for '{song['name']}'.")
    # aubio
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_tracking(song_a['path'], sample_rate)
    # aubio with lpf before
    #times_of_beats_a, bpm_a = beat_track.aubio_beat_track_with_lpf_before(config, song_a['path'], sample_rate)
    # librosa with start times
    #times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking(signal_a, sample_rate)
    # librosa with mono signal input --> best results
    times_of_beats, stop_times_of_beats = beat_track.librosa_beat_tracking_with_mono_signal(config, song)

    # split song into clip segments of even number of consecutive beats
    print("INFO - Analysis: Creating segments for comparison.")
    areas, clips = segment_song(config, mono_signal, times_of_beats)

    # score segments using segment_scorer utility class
    segment_scores = scorer.score_segments(config, clips, areas, bias_mode=bias_mode)

    #print(f"segment scores: length of 1: {len(segment_scores_a)}, 2: {len(segment_scores_b)}")

    # determine best transition candidates
    best_segment_index_a = segment_scores.tolist().index(min(segment_scores))

    #print(f"Selected indexes for songs A: {best_segment_index_a}, B: {best_segment_index_b}")
    #print(segment_times1)

    return areas[best_segment_index_a]


def get_transition_points(config, song_a, song_b):
    # song A: last part of song
    transition_points_a = find_best_segments(config, song_a, False)

    # song B: first part of song
    transition_points_b = find_best_segments(config, song_b, True)

    transition_points['c'] = transition_points_a[0]
    transition_points['d'] = transition_points_a[1]
    transition_points['e'] = transition_points_a[2]
    transition_points['a'] = transition_points_b[0]
    transition_points['b'] = transition_points_b[1]
    transition_points['x'] = transition_points_b[2]
    #transition_points['b'] = round(transition_points['a'] + (transition_points['d'] - transition_points['c']), 3)
    #transition_points['x'] = round(transition_points['a'] + (transition_points['e'] - transition_points['c']), 3)

    # TSL = Transition Segment Length
    tsl_list = [config['transition_midpoint'], config['transition_length']-config['transition_midpoint']]

    return transition_points, tsl_list
