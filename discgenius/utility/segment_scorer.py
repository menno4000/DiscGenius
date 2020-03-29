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


async def calculate_similarity_scores(si, clip_stfts, step_size, clip_size, midpoint, transition_length):
    score_first = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size], clip_stfts[si*step_size + i]) for i in range(0, int(midpoint/clip_size))])
    score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size + midpoint], clip_stfts[si*step_size + i]) for i in range(int(midpoint/clip_size), int(transition_length/clip_size-1))])

    # if scores of two segments are similar, then they are suitable for transition
    # todo: check if scores are small which gives bonus
    if score_second > score_first:
        ratio = score_second/score_first - 1
    else:
        ratio = score_first/score_second - 1
    print(f"si: {si}, scores: {score_first}, {score_second}, ratio: {ratio}")
    return ratio


# calculates segment scores for a list of beat clips
def score_segments(config, clips, areas, transition_length, midpoint, clip_size, step_size, bias_mode=False):
    scores = {}
    mix_area_a = config['mix_area']
    mix_area_b = 1 - mix_area_a
    clip_stfts = [calc_stft_averages(numpy.abs(librosa.stft(clips[i]))) for i in range(0, len(areas))]

    # only compute scores for a part of song depending on bias mode
    if bias_mode:
        iterations = int(len(areas)*mix_area_a)

        print(f"INFO - Analysis: Rating & comparing segments for first part of song A.")
        print(f"\t\tAmount of areas: {len(areas)}, amount of clips: {len(clips)}. Running {iterations} iterations.")

        for si in range(0, iterations):
        #    scores['si'] = asyncio.run(calculate_similarity_scores(si, clip_stfts, step_size, clip_size, midpoint, transition_length))
            score_first = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size], clip_stfts[si*step_size + i]) for i in range(1, int(midpoint/clip_size))])
            score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size], clip_stfts[si*step_size + i]) for i in range(int(midpoint/clip_size), int(transition_length/clip_size-1))])

            # if scores of two segments are similar, then they are suitable for transition
            # todo: check if scores are small which gives bonus
            score = score_first + score_second
            if score_second > score_first:
                ratio = score_second/score_first - 1
            else:
                ratio = score_first/score_second - 1
            #print(f"si: {si}, scores: {score_first}, {score_second}, ratio: {ratio}")
            scores[si] = score# * ratio

        # dummy values to skip last two thirds
        for si in range(int(len(areas)*mix_area_a), len(areas)):
            scores[si] = 1000
    else:
        # dummy values to skip first two thirds
        for si in range(0, (int(len(areas)*mix_area_b))):
            scores[si] = 1000

        print(f"INFO - Analysis: Rating & comparing segments for last part of song A.")
        print(f"\t\tAmount of areas: {len(areas)}, amount of clips: {len(clips)}. Running {int(len(areas) * mix_area_a)} iterations.")
        print(f"using indexes: {int(len(areas)*mix_area_b)}-{len(areas)}")

        for si in range(int(len(areas)*mix_area_b), len(areas)):
            score_first = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size], clip_stfts[si*step_size + i]) for i in range(1, int(midpoint/clip_size))])
            score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si*step_size], clip_stfts[si*step_size + i]) for i in range(int(midpoint/clip_size), int(transition_length/clip_size-1))])

            # if scores of two segments are similar, then they are suitable for transition
            score = score_first + score_second
            if score_second > score_first:
                ratio = score_second/score_first - 1
            else:
                ratio = score_first/score_second - 1
            #print(f"si: {si}, scores: {score_first}, {score_second}, ratio: {ratio}")
            scores[si] = score# * ratio

    return scores