#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# scenarios.py contains different transition scenarios and has two methods per scenario
# it will manipulate the frame_arrays using methods from the 'sound_manipulation' script

__author__ = "Oskar Sailer"

import numpy as np

from .utility import sound_manipulation as sm


def chunks(l, n):
    n = max(1, n)
    return (l[i:i + n] for i in range(0, len(l), n))


def vff_1_segment_1(frame_array_a, frame_array_b, scenario):
    # volume fading factor
    vff = scenario['vff']
    steps = int(len(vff)/2)

    # cut segment into two pieces for smoother transition
    frames_per_step = int(len(frame_array_a) / steps)
    frame_array_a_edited = []
    frame_array_b_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly decrease volume of Song A, increase volume of Song B
    i = 0
    for segment_a, segment_b in zip(frame_array_a_segmented, frame_array_b_segmented):
        frame_array_a_edited.append(sm.edit_volume_by_factor(segment_a, vff[i]))
        frame_array_b_edited.append(sm.edit_volume_by_factor(segment_b, vff[len(vff)-i-1]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)
    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # EQ: cut low's of Song B
    frame_array_b_edited = sm.low_cut_filter(frame_array_b_edited, order=3)

    return frame_array_a_edited, frame_array_b_edited


def vff_1_segment_2(frame_array_a, frame_array_b, scenario):
    vff = scenario['vff']
    steps = int(len(vff)/2)

    # cut segment into two pieces for smoother transition
    frames_per_step = int(len(frame_array_a) / steps)
    frame_array_a_edited = []
    frame_array_b_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly decrease volume of Song A, increase volume of Song B
    i = 0
    for segment_a, segment_b in zip(frame_array_a_segmented, frame_array_b_segmented):
        frame_array_a_edited.append(sm.edit_volume_by_factor(segment_a, vff[len(vff)-i-1]))
        frame_array_b_edited.append(sm.edit_volume_by_factor(segment_b, vff[i]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)
    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # EQ: cut low's of Song A
    frame_array_a_edited = sm.low_cut_filter(frame_array_a_edited, order=3)

    return frame_array_a_edited, frame_array_b_edited


def EQ_1_segment_1_dynamic(frame_array_a, frame_array_b, scenario):
    # EQGF = EQ gain factor
    eqgf_a_list = scenario['eqgf_a']
    eqgf_b_list = scenario['eqgf_b']
    steps = int(len(eqgf_a_list)/2)

    # cut segment into pieces for smoother transition
    frames_per_step = int(len(frame_array_a) / steps)
    frame_array_a_edited = []
    frame_array_b_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly decrease EQ for mid's & high's of Song A, increase EQ for mid's & high's of Song B
    i = 0
    for segment_a, segment_b in zip(frame_array_a_segmented, frame_array_b_segmented):
        frame_array_a_edited.append(sm.modify_mids_and_highs_by_gain(segment_a, eqgf_a_list[i]))
        frame_array_b_edited.append(sm.modify_mids_and_highs_by_gain(segment_b, eqgf_b_list[i]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)
    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # EQ: cut low's of Song B to -26
    frame_array_b_edited = sm.low_shelf_filter(frame_array_b_edited, -26)

    return frame_array_a_edited, frame_array_b_edited


def EQ_1_segment_2_dynamic(frame_array_a, frame_array_b, scenario):
    eqgf_a_list = scenario['eqgf_a']
    eqgf_b_list = scenario['eqgf_b']
    steps = int(len(eqgf_a_list)/2)

    # cut segment into pieces for smoother transition
    frames_per_step = int(len(frame_array_a) / steps)
    frame_array_a_edited = []
    frame_array_b_edited = []
    frame_array_a_segmented = chunks(frame_array_a, frames_per_step)
    frame_array_b_segmented = chunks(frame_array_b, frames_per_step)

    # slowly decrease EQ for mid's & highs' of Song A, increase EQ for mid's & high's of Song B
    i = 0 + steps
    for segment_a, segment_b in zip(frame_array_a_segmented, frame_array_b_segmented):
        if i > len(eqgf_a_list)-1:  # necessary because sometime a single frame is the last (additional) separated segment
            i = len(eqgf_a_list)-1
        frame_array_a_edited.append(sm.modify_mids_and_highs_by_gain(segment_a, eqgf_a_list[i]))
        frame_array_b_edited.append(sm.modify_mids_and_highs_by_gain(segment_b, eqgf_b_list[i]))
        i += 1

    frame_array_a_edited = np.concatenate(frame_array_a_edited)
    frame_array_b_edited = np.concatenate(frame_array_b_edited)

    # EQ: cut lows of Song A to -26
    frame_array_a_edited = sm.low_shelf_filter(frame_array_a_edited, -26)

    return frame_array_a_edited, frame_array_b_edited


def low_cut_segment(frame_array):
    return sm.low_shelf_filter(frame_array, -26)
