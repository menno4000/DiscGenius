import librosa
import librosa.display
from scipy.spatial import distance
import numpy
import asyncio
import matplotlib.pyplot as plt

#calculates the averages of a librosa stft output
def calc_stft_averages(stft):
    return [numpy.average(t) for t in stft]

#calculates the euclidean distance of two full signal stft ouputs
def calc_euclidean_distance(stft1, stft2):

    euclidean_distances = []
    for index in range(0, (len(stft1)-1)):
        euclidean_distances.append(distance.euclidean(stft1[index], stft2[index]))
    return numpy.average(euclidean_distances)


def calculate_scores(config, stfts_clips, areas, boundaries):
    # dummy scores to skip last two thirds
    scores = numpy.full(len(areas), 1000)

    clip_size = config['clip_size']
    step_size = config['step_size']
    transition_length = config['transition_length']
    midpoint = config['transition_midpoint']
    transition_segment_length_1 = midpoint
    transition_segment_length_2 = transition_length - midpoint

    # area that is eligible for transition will get better scores
    for si in range(boundaries[0], boundaries[1]):
        score_first = numpy.sum([calc_euclidean_distance(stfts_clips[si*step_size], stfts_clips[si*step_size + (i+1) * clip_size]) for i in range(0, int(transition_segment_length_1/clip_size))])
        score_second = numpy.sum([calc_euclidean_distance(stfts_clips[si*step_size + midpoint], stfts_clips[si*step_size + midpoint + (i+1) * clip_size]) for i in range(0, int(transition_segment_length_2/clip_size))])
        scores[si] = score_first + score_second
    return scores


# calculates segment scores for a list of beat clips
def score_segments(config, clips, areas, bias_mode=False):
    mix_area_a = config['mix_area']
    mix_area_b = 1 - mix_area_a

    clip_stfts = [calc_stft_averages(numpy.abs(librosa.stft(clips[i]))) for i in range(0, len(clips))]
    iterations = int(len(areas)*mix_area_a)

    # bias mode defines whether song is ending or starting in transition
    # depending on that only first or last part will be analyzed
    if bias_mode:
        boundaries = [0, iterations]
        print(f"INFO - Analysis: Rating & comparing segments for first part of song B.")
    else:
        boundaries = [int(len(areas)*mix_area_b), len(areas)]
        print(f"INFO - Analysis: Rating & comparing segments for last part of song A.")

    print(f"\t\t Amount of areas: {len(areas)}, amount of clips: {len(clips)}, mix area value: {mix_area_a}.")
    print(f"\t\t Running {iterations} iterations, using indexes {boundaries[0]} - {boundaries[1]}.")

    scores = calculate_scores(config, clip_stfts, areas, boundaries)
    return scores