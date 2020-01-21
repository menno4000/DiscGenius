#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# evaluator.py will take the results from the analysis.py and pick segments that will be used for the transition
# it will define the transition points and the length of the two transition segments

# TSL = Transition Segment Length
# tsl_list = [48, 16]
tsl_list = [32, 32]

# --- andromeda to 86 --- C-D-E: 5:24-6:24:7:23 --- 32-32
transition_points = {
    'a': 15.115,
    'c': 324.95,
    'd': 384.02,
    'e': 443.10
}


def evaluate_segments(config):
    global tsl_list
    global transition_points
    # placeholder until analysis provides results
    # then song information about segments will be imported from csv file

    transition_points['b'] = round(transition_points['a'] + (transition_points['d'] - transition_points['c']), 3)
    transition_points['x'] = round(transition_points['a'] + (transition_points['e'] - transition_points['c']), 3)

    return tsl_list, transition_points


def get_evaluation_points():
    return {'tsl_list': tsl_list, 'transition_points': transition_points}


def set_evaluation_points(tsl_list_new, transition_points_new):
    global tsl_list
    global transition_points

    tsl_list = tsl_list_new
    transition_points = transition_points_new
    return {'tsl_list': tsl_list, 'transition_points': transition_points}
