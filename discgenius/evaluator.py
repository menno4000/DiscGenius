#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# evaluator.py will take the results from the analysis.py and pick segments that will be used for the transition
# it will define the transition points and the length of the two transition segments

# TSL = Transition Segment Length
tsl_list = [1, 1]


def evaluate_segments(config, transition_points):
    transition_points['b'] = round(transition_points['a'] + (transition_points['d'] - transition_points['c']), 3)
    transition_points['x'] = round(transition_points['a'] + (transition_points['e'] - transition_points['c']), 3)
    tsl_list[0] = (config['transition_midpoint'])
    tsl_list[1] = (config['transition_length']-config['transition_midpoint'])

    return tsl_list, transition_points


def get_evaluation_points():
    return {'tsl_list': tsl_list, 'transition_points': transition_points}


def set_evaluation_points(tsl_list_new, transition_points_new):
    tsl_list = tsl_list_new
    transition_points = transition_points_new
    return {'tsl_list': tsl_list, 'transition_points': transition_points}
