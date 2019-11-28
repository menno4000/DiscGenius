#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# scenarios.py contains different transition scenarios and has two methods per scenario
# it will manipulate the frame_arrays using methods from the 'sound_manipulation' script

__author__ = "Oskar Sailer"

import numpy as np
import sound_manipulation as sm

# vff = volume fading factor
VFF_LIST = [0.8, 0.7, 0.6, 0.5]

# EQGF = EQ gain factor - used for development of mid&high bands in transition
# Song A goes '-->' and song B goes '<--' along that list to continually decrease/increase in volume
EQGF_LIST = [-2, -3.5, -7, -10]

# smooth
EQGF_A_LIST_8_STEPS = [-0.5,    -1,     -1.7,   -2.8,   -3.5,   -5.5,   -7.5,   -9.5]
EQGF_B_LIST_8_STEPS = [-20,     -16,    -10,    -7.5,   -5.5,   -4,     -2.6,   -1]


def chunks(l, n):
    n = max(1, n)
    return (l[i:i + n] for i in range(0, len(l), n))


def transition_scenario_1_segment_1(frame_array_a, frame_array_b, tsl_1):
    # --- modifying Song A ---
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a) // 2]
    frame_array_a_2 = frame_array_a[len(frame_array_a) // 2:]

    # slowly decrease volume of Song A
    frame_array_a_1 = sm.edit_volume_by_factor(frame_array_a_1, VFF_LIST[0])
    frame_array_a_2 = sm.edit_volume_by_factor(frame_array_a_2, VFF_LIST[1])

    # cut bass from last bar from Song A for smoother transition
    frame_array_a_2 = sm.cut_bass_for_last_bar(frame_array_a_2, tsl_1 / 2)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b) // 2]
    frame_array_b_2 = frame_array_b[len(frame_array_b) // 2:]

    # slowly increase volume of Song B & remove Bass
    frame_array_b_1 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_b_1, VFF_LIST[3]), order=3)
    frame_array_b_2 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_b_2, VFF_LIST[2]), order=3)

    # merge both pieces again
    return np.append(frame_array_a_1, frame_array_a_2), np.append(frame_array_b_1, frame_array_b_2)


def transition_scenario_1_segment_2(frame_array_a, frame_array_b, tsl_2):
    # --- modifying Song A ---
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a) // 2]
    frame_array_a_2 = frame_array_a[len(frame_array_a) // 2:]

    # slowly decrease volume of Song A & remove Bass
    frame_array_a_1 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_a_1, VFF_LIST[2]), order=3)
    frame_array_a_2 = sm.low_cut_filter(sm.edit_volume_by_factor(frame_array_a_2, VFF_LIST[3]), order=3)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b) // 2]
    frame_array_b_2 = frame_array_b[len(frame_array_b) // 2:]

    # slowly increase volume of Song B
    frame_array_b_1 = sm.edit_volume_by_factor(frame_array_b_1, VFF_LIST[1])
    frame_array_b_2 = sm.edit_volume_by_factor(frame_array_b_2, VFF_LIST[0])

    # cut bass from last bar from Song B for smoother transition
    frame_array_b_2 = sm.cut_bass_for_last_bar(frame_array_b_2, tsl_2 / 2)

    # merge both pieces again
    return np.append(frame_array_a_1, frame_array_a_2), np.append(frame_array_b_1, frame_array_b_2)


def transition_scenario_2_segment_1(frame_array_a, frame_array_b, tsl_1):
    # --- modifying Song A ---
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a) // 2]
    frame_array_a_2 = frame_array_a[len(frame_array_a) // 2:]

    # slowly decrease EQ for mids & highs of Song A
    frame_array_a_1 = sm.modify_mids_and_highs_by_gain(frame_array_a_1, EQGF_LIST[0])
    frame_array_a_2 = sm.modify_mids_and_highs_by_gain(frame_array_a_2, EQGF_LIST[1])

    # cut bass from last bar from Song A for smoother transition
    frame_array_a_2 = sm.cut_bass_for_last_bar(frame_array_a_2, tsl_1 / 2)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b) // 2]
    frame_array_b_2 = frame_array_b[len(frame_array_b) // 2:]

    # slowly increase EQ for mids & highs of Song B & remove Bass
    frame_array_b_1 = sm.modify_mids_and_highs_by_gain(frame_array_b_1, EQGF_LIST[3])
    frame_array_b_2 = sm.modify_mids_and_highs_by_gain(frame_array_b_2, EQGF_LIST[2])

    # EQ lows of Song B to -26
    frame_array_b_1 = sm.low_shelf_filter(frame_array_b_1, -26)
    frame_array_b_2 = sm.low_shelf_filter(frame_array_b_2, -26)

    # merge both pieces again
    return np.append(frame_array_a_1, frame_array_a_2), np.append(frame_array_b_1, frame_array_b_2)


def transition_scenario_2_segment_2(frame_array_a, frame_array_b, tsl_1):
    # cut segment into two pieces for smoother transition
    frame_array_a_1 = frame_array_a[:len(frame_array_a) // 2]
    frame_array_a_2 = frame_array_a[len(frame_array_a) // 2:]

    # slowly decrease volume of Song A & remove Bass
    frame_array_a_1 = sm.modify_mids_and_highs_by_gain(frame_array_a_1, EQGF_LIST[2])
    frame_array_a_2 = sm.modify_mids_and_highs_by_gain(frame_array_a_2, EQGF_LIST[3])

    # EQ lows of Song A to -26
    frame_array_a_1 = sm.low_shelf_filter(frame_array_a_1, -26)
    frame_array_a_2 = sm.low_shelf_filter(frame_array_a_2, -26)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_1 = frame_array_b[:len(frame_array_b) // 2]
    frame_array_b_2 = frame_array_b[len(frame_array_b) // 2:]

    # slowly increase volume of Song B
    frame_array_b_1 = sm.modify_mids_and_highs_by_gain(frame_array_b_1, EQGF_LIST[1])
    frame_array_b_2 = sm.modify_mids_and_highs_by_gain(frame_array_b_2, EQGF_LIST[0])

    # cut bass from last bar from Song B for smoother transition
    frame_array_b_2 = sm.cut_bass_for_last_bar(frame_array_b_2, tsl_1 / 2)

    # merge both pieces again
    return np.append(frame_array_a_1, frame_array_a_2), np.append(frame_array_b_1, frame_array_b_2)


def transition_scenario_2_segment_1_dynamic(frame_array_a, frame_array_b, tsl_1):
    # --- modifying Song A ---
    # cut segment into pieces for smoother transition
    steps = 4
    frames_per_step = int(len(frame_array_a) / steps)

    frame_array_a_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)

    # slowly decrease EQ for mids & highs of Song A
    i = 0
    for segment in frame_array_a_segmented:
        frame_array_a_edited.append(sm.modify_mids_and_highs_by_gain(segment, EQGF_A_LIST_8_STEPS[i]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)

    # cut bass from last bar from Song A for smoother transition
    frame_array_a_edited = sm.cut_bass_for_last_bar(frame_array_a_edited, tsl_1)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_edited = []
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly increase EQ for mids & highs of Song B & remove Bass
    i = 0
    for segment in frame_array_b_segmented:
        frame_array_b_edited.append(sm.modify_mids_and_highs_by_gain(segment, EQGF_B_LIST_8_STEPS[i]))
        i += 1

    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # EQ: cut lows of Song B to -26
    frame_array_b_edited = sm.low_shelf_filter(frame_array_b_edited, -26)

    # merge both pieces again
    return frame_array_a_edited, frame_array_b_edited


def transition_scenario_2_segment_2_dynamic(frame_array_a, frame_array_b, tsl_2):
    # --- modifying Song A ---
    # cut segment into pieces for smoother transition
    steps = 4
    frames_per_step = int(len(frame_array_a) / steps)

    frame_array_a_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)

    # slowly decrease EQ for mids & highs of Song A
    i = 0 + steps
    for segment in frame_array_a_segmented:
        if i > 7:  # necessary because sometime a single frame is the last (additional) separated segment
            i = 7
        frame_array_a_edited.append(sm.modify_mids_and_highs_by_gain(segment, EQGF_A_LIST_8_STEPS[i]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)

    # EQ: cut lows of Song A to -26
    frame_array_a_edited = sm.low_shelf_filter(frame_array_a_edited, -26)

    # --- modifying Song B ---
    # cut segment into two pieces for smoother transition
    frame_array_b_edited = []
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly increase EQ for mids & highs of Song B & remove Bass
    i = 0 + steps
    for segment in frame_array_b_segmented:
        if i > 7:
            i = 7
        frame_array_b_edited.append(sm.modify_mids_and_highs_by_gain(segment, EQGF_B_LIST_8_STEPS[i]))
        i += 1

    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # cut bass from last bar from Song B for smoother transition
    frame_array_b_edited = sm.cut_bass_for_last_bar(frame_array_b_edited, tsl_2)

    # merge both pieces again
    return frame_array_a_edited, frame_array_b_edited


def low_cut_segment(frame_array):
    return sm.low_shelf_filter(frame_array, -26)

