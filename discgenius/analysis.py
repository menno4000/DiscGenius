import librosa
import librosa.display
from scipy.spatial import distance
import numpy
import matplotlib.pyplot as plt

from .utility import segment_scorer as scorer

hop_length = 512
segment_size = 16

transition_points = {}


#calculates transition points dictionary for a transition of given between two given songs
def get_transition_points(config, song_a, song_b, transition_length):

    signal1, rate1 = librosa.load(f"{config['data_path']}/{song_a['name']}", sr=config['sample_rate'])
    signal2, rate2 = librosa.load(f"{config['data_path']}/{song_b['name']}", sr=config['sample_rate'])

    #compute onset environments
    onset_env1 = librosa.onset.onset_strength(y=signal1, sr=rate1, aggregate=numpy.median)
    onset_env2 = librosa.onset.onset_strength(y=signal2, sr=rate2, aggregate=numpy.median)

    #derive time for sample index from onset environments
    times1 = librosa.times_like(onset_env1, sr=rate1, hop_length=hop_length)
    times2 = librosa.times_like(onset_env2, sr=rate2, hop_length=hop_length)

    #compute beats using librosa beat tracking
    tempo1, beats1 = librosa.beat.beat_track(y=signal1, sr=rate1)
    tempo2, beats2 = librosa.beat.beat_track(y=signal2, sr=rate2)

    #create onset sample matrix from tracked beats
    onset_samples1 = list(librosa.frames_to_samples(beats1))
    onset_samples1 = numpy.concatenate(onset_samples1, len(signal1))
    onset_samples2 = list(librosa.frames_to_samples(beats2))
    onset_samples2 = numpy.concatenate(onset_samples2, len(signal2))

    #derive frame index of beat starts/stops from onset sample matrix
    starts1 = onset_samples1[0:-1]
    stops1 = onset_samples1[1:]
    starts2 = onset_samples2[0:-1]
    stops2 = onset_samples2[1:]

    times_starts1 = librosa.samples_to_time(starts1, sr=rate1)
    times_stops1 = librosa.samples_to_time(stops1, sr=rate1)
    times_starts2 = librosa.samples_to_time(starts2, sr=rate1)
    times_stops2 = librosa.samples_to_time(stops2, sr=rate1)

    #split song into clip segments of even number of consecutive beats
    clips1 = []
    clips2 = []

    segment_times1 = {}
    segment_times2 = {}

    for i in range(0, (len(times_stops1)-segment_size), segment_size):
        clip = signal1[starts1[i]:stops1[i+segment_size]]
        clips1.append(clip)
        #TODO rework
        segment_times1[int(i/segment_size)] = [((times_starts1[i]+times_stops1[i])/2), ((times_starts1[i+segment_size]+times_stops1[i+segment_size])/2)]

    for i in range(0, (len(times_stops2)-segment_size), segment_size):
        clip = signal2[starts2[i]:stops2[i+segment_size]]
        clips2.append(clip)
        segment_times2[int(i/segment_size)] = [((times_starts2[i]+times_stops2[i])/2), ((times_starts2[i+segment_size]+times_stops2[i+segment_size])/2)]

    #score segments using segment_scorer utility class
    segment_scores1 = scorer.score_segments(clips1, transition_length, False)
    segment_scores2 = scorer.score_segments(clips2, transition_length, True)

    #determine best transition candidates
    best_segment_index1 = segment_scores1.index(min(segment_scores1))
    best_segment_index2 = segment_scores2.index(min(segment_scores2))

    #start of transition in song A
    #start of transition in song A
    transition_points['c'] = ((segment_times1[best_segment_index1][0]+segment_times1[best_segment_index1][1])/2)
    #midpoint of transition in song A
    transition_points['d'] = ((segment_times1[best_segment_index1+3][0]+segment_times1[best_segment_index1+3][1])/2)
    #end of transition in song A
    transition_points['e'] = ((segment_times1[best_segment_index1+7][0]+segment_times1[best_segment_index1+7][1])/2)
    #start of transition in song B
    transition_points['a'] = ((segment_times2[best_segment_index2][0]+segment_times2[best_segment_index2][1])/2)
    #midpoint of transition in song B
    transition_points['b'] = ((segment_times2[best_segment_index2+3][0]+segment_times2[best_segment_index2+3][1])/2)
    #end of transition in song B
    transition_points['x'] = ((segment_times2[best_segment_index2+7][0]+segment_times2[best_segment_index2+7][1])/2)

    return transition_points
