import librosa
import librosa.display
from scipy.spatial import distance
import numpy
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

#calculates segment scores for a list of beat clips
def score_segments(clips, segment_length, midpoint, bias_mode=False):
    scores = []

    #only compute scores for first or last third of song depending on bias mode
    if bias_mode:
        clip_stfts = [calc_stft_averages(numpy.abs(librosa.stft(clips[i]))) for i in range(0, (int(len(clips)*0.33)+segment_length))]
        for si in range (0, (int(len(clips)*0.33))):
            if midpoint > 2:
                score_first = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(1, (midpoint-1))])
                score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(midpoint, (segment_length-1))])
            else:
                score_first = calc_euclidean_distance(clip_stfts[si], clip_stfts[si+1])
                score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(midpoint, (segment_length-1))])


            score = score_first + score_second

            scores.append(score)
        for si in range (int(len(clips)*0.33), (len(clips)-segment_length)):
            scores.append(100)
    else:
        clip_stfts = [calc_stft_averages(numpy.abs(librosa.stft(clips[i]))) for i in range(0, len(clips))]

        for si in range (0, (int(len(clips)*0.66))):
            scores.append(100)
        for si in range (int(len(clips)*0.66), (len(clips)-(segment_length))):
            if midpoint > 2:
                score_first = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(1, (midpoint-1))])
                score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(midpoint, (segment_length-1))])
            else:
                score_first = calc_euclidean_distance(clip_stfts[si], clip_stfts[si+1])
                score_second = numpy.sum([calc_euclidean_distance(clip_stfts[si], clip_stfts[si+i]) for i in range(midpoint, (segment_length-1))])


            score = score_first + score_second

            scores.append(score)
    return scores
