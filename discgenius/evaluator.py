#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# evaluator.py will take the results from the analysis.py and pick segments that will be used for the transition
# it will define the transition points and the length of the two transition segments


def evaluate_segments(config):
    # placeholder until analysis provides results
    # then song information about segments will be imported from csv file

    # TSL = Transition Segment Length
    # tsl_list = [48, 16]
    tsl_list = [32, 32]

    transition_points = {
        'a': 15.115,
        'c': 324.95,
        'd': 384.02,
        'e': 443.10
    }
    transition_points['b'] = round(transition_points['a'] + (transition_points['d'] - transition_points['c']), 3)
    transition_points['x'] = round(transition_points['a'] + (transition_points['e'] - transition_points['c']), 3)

    return tsl_list, transition_points
