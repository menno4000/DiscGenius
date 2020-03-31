from fastapi import HTTPException

from . import utility as util


def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


def convert_bpm(config, bpm):
    if bpm == 0.0:
        return bpm
    try:
        bpm = float(bpm)
        if bpm < config['min_bpm'] or bpm > config['max_bpm']:
            raise_exception(400, f"Please set a bpm value between {config['min_bpm']} and {config['max_bpm']}.")
        return bpm

    except ValueError:
        raise_exception(400, "Please provide a float-number as bpm value.")


def validate_transition_times(config, transition_length, transition_midpoint, transition_points, mix_bpm, song_a_name,
                              song_b_name):
    if not transition_points:
        if transition_length < 2 or transition_length > 256:
            raise_exception(400, "Transition length should be greater then one and not bigger then 256.")
        if transition_midpoint == 1337:
            transition_midpoint = transition_length / 2
        if transition_midpoint > transition_length or transition_midpoint < 0:
            raise_exception(400, f"Transition midpoint should be between zero and given transition length ({transition_length}).")
        return transition_length, transition_length, None

    # check if given points are in chronological order & bigger then set minimum
    min_time = config['min_segment_time']
    if transition_points['e'] - transition_points['d'] < min_time or transition_points['d'] - transition_points[
        'c'] < min_time:
        raise_exception(400, "Please make the time frame between transition points bigger.")

    # recalculate transition length & midpoint
    transition_length_time = transition_points['e'] - transition_points['c']
    beat_length = 60 / mix_bpm
    transition_length_beats = int(round(transition_length_time / beat_length, 0))

    transition_midpoint_length = transition_points['d'] - transition_points['c']
    transition_midpoint_beats = int(round(transition_midpoint_length / beat_length, 0))

    # check if points are in songs
    song_a_length = util.get_length_of_song(config, song_a_name)
    song_b_length = util.get_length_of_song(config, song_b_name)

    boundary_a = song_a_length - transition_points['e']
    boundary_b = song_b_length - transition_points['a'] - transition_length_time
    if boundary_a < 0 or boundary_b < 0:
        raise_exception(400, f"The given transition points are to big for the provided songs. \n"
                             f"Length of A: {round(song_a_length, 3)}s, B: {round(song_b_length, 3)}s.\n"
                             f"Boundaries A (Length-E): {boundary_a}, B (Length-A-Trans_length): {boundary_b}")

    return transition_length_beats, transition_midpoint_beats, transition_points


def validate_bpms(config, song_a_name, song_b_name, desired_bpm):
    bpm_a = convert_bpm(config, util.get_bpm_from_filename(song_a_name))
    bpm_b = convert_bpm(config, util.get_bpm_from_filename(song_b_name))
    desired_bpm = convert_bpm(config, desired_bpm)
    if desired_bpm == 0.0:
        desired_bpm = bpm_a

    if abs(bpm_a - bpm_b) > config['max_bpm_diff']:
        raise_exception(400, f"Please use songs that have similar BPM. Max diff is {config['max_bpm_diff']}")
    if abs(bpm_a - desired_bpm) > config['max_bpm_diff'] or abs(bpm_b - desired_bpm) > config['max_bpm_diff']:
        raise_exception(400, f"Please use a different value for your desired BPM. Max diff is {config['max_bpm_diff']}")

    return bpm_a, bpm_b, desired_bpm
