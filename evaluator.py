#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# evaluator.py will take the results from the analysis.py and pick segments that will be used for the transition
# it will define the transition points and the length of the two transition segments


__author__ = "Oskar Sailer"

SAMPLE_RATE = 44100


def evaluate_segments():
    # placeholder until analysis provides results
    # then song information about segments will be imported from csv file

    # TSL = Transition Segment Length
    tsl_list = [32, 32]

    transition_points = {
        'a': 56 + 0.275,
        'c': 300 + 4 + 0.575,
        'd': 300 + 57 + 0.533,
        'e': 360 + 50 + 0.5
    }
    transition_points['b'] = transition_points['a'] + (transition_points['d'] - transition_points['c'])
    transition_points['x'] = transition_points['a'] + (transition_points['e'] - transition_points['c'])

    return tsl_list, transition_points
