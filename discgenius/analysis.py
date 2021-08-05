from .utility import beat_track
from .utility import segment_scorer as scorer
from .utility import utility as util
import logging

logger = logging.getLogger("analysis")
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
def find_best_segments(config, song, tsl_list, bias_mode, entry_point):
    mono_signal = song['mono']

    logger.info(f"INFO - Analysis: Beat detection for '{song['name']}'.")
    # # aubio
    # times_of_beats_a, bpm_a = beat_track.aubio_beat_tracking(song_a['path'], sample_rate)
    # # aubio with lpf before
    # times_of_beats_a, bpm_a = beat_track.aubio_beat_track_with_lpf_before(config, song_a['path'], sample_rate)
    # # librosa with start times
    # times_of_beats_a, stop_times_of_beats_a = beat_track.librosa_beat_tracking(signal_a, sample_rate)
    # librosa with mono signal input --> best results
    times_of_beats, stop_times_of_beats = beat_track.librosa_beat_tracking_with_mono_signal(config, song, entry_point)

    # split song into clip segments of even number of consecutive beats
    logger.info("INFO - Analysis: Creating segments for comparison.")
    areas, clips = segment_song(config, mono_signal, times_of_beats)

    # score segments using segment_scorer utility class
    segment_scores = scorer.score_segments(config, clips, areas, entry_point, bias_mode=bias_mode)

    #logger.info(f"segment scores: length of 1: {len(segment_scores_a)}, 2: {len(segment_scores_b)}")

    # determine best transition candidates
    best_segment_index = segment_scores.tolist().index(min(segment_scores))

    #logger.info(f"Selected indexes for songs A: {best_segment_index_a}, B: {best_segment_index_b}")
    #logger.info(segment_times1)#

    transition_points = {}

    if bias_mode:
        transition_points['a'] = areas[best_segment_index][0]
        transition_points['b'] = areas[best_segment_index][1]
        transition_points['x'] = areas[best_segment_index][2]
    else:
        transition_points['c'] = areas[best_segment_index][0]
        transition_points['d'] = areas[best_segment_index][1]
        transition_points['e'] = areas[best_segment_index][2]

    util.save_song_analysis_data(config, song, transition_points, tsl_list)
    return transition_points


def get_transition_points(config, song_a, song_b, exit_point, entry_point, tsl_list):

    # song A: last part of song --> bias_mode = False (C-D-E)
    # check if analysis was already done
    transition_points_a = util.read_song_analysis_data(config, song_a, tsl_list, False)
    if not transition_points_a:
        transition_points_a = find_best_segments(config, song_a, tsl_list, False, exit_point)

    # song B: first part of song --> bias_mode = True (A-B-X)
    transition_points_b = util.read_song_analysis_data(config, song_b, tsl_list, True)
    if not transition_points_b:

        transition_points_b = find_best_segments(config, song_b, tsl_list, True, entry_point)

    return {**transition_points_a, **transition_points_b}
