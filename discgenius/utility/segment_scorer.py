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
    stft1_averages = calc_stft_averages(stft1)
    stft2_averages = calc_stft_averages(stft2)
    euclidean_distances = []
    for index in range(0, (len(stft1_averages)-1)):
        euclidean_distances.append(distance.euclidean(stft1_averages[index], stft2_averages[index]))
    return numpy.average(euclidean_distances)

#calculates segment scores for a list of beat clips
def score_segments(clips, segment_length, bias_mode=False):
    scores = []
    for si in range (0, (len(clips)-int(segment_length))):
        clip_stfts = [numpy.abs(librosa.stft(clips[i])) for i in range(si, (si+(int(segment_length)-1)))]
        score = numpy.sum([calc_euclidean_distance(clip_stfts[0], clip_stfts[i]) for i in range(1,(int(segment_length)-1))])


        scores.append(score)

    #bias pro first half if entry point is sought
    if bias_mode:
        for i in range (0, (round((len(scores)/2)))):
            scores[i] = scores[i]*0.1
    else:
        for i in range((round((len(scores)/2))), len(scores)):
            scores[i] = scores[i]*0.1
    return scores
