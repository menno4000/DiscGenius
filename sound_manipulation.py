import math

import evaluator
import numpy as np
import scipy as sp
from scipy.signal import butter, lfilter


################################################################ filter types ################################################################


def high_cut_filter(data, order=5):
    type = 'low'
    cutoff = 2000

    nyq = 0.5 * evaluator.SAMPLE_RATE
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=type, analog=False)
    frames = lfilter(b, a, data)
    return frames.astype('float32')


def low_cut_filter(data, order=5):
    type = 'high'
    cutoff = 200

    nyq = 0.5 * evaluator.SAMPLE_RATE
    normal_cutoff = cutoff / nyq
    # normal_cutoff = 0.009
    b, a = butter(order, normal_cutoff, btype=type, analog=False)
    frames = lfilter(b, a, data)
    return frames.astype('float32')


def bandstop_filter(data, order):
    type = 'bandstop'
    freq_values = [200, 2000]
    b, a = butter(order, freq_values, btype=type, analog=False)
    frames = lfilter(b, a, data)
    return frames


# used for high EQ'ing
def high_shelf_filter(frame_array, gain, freq_cut=2000):
    frequency_cutoff = freq_cut
    volume_gain = gain

    K = math.tan(math.pi * frequency_cutoff / evaluator.SAMPLE_RATE)
    G = 10 ** (volume_gain / 20)

    # calculating parameters
    b0 = (G + math.sqrt(2 * G) * K + (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)
    b1 = (2 * ((K ** 2) - G)) / (1 + math.sqrt(2) * K + K ** 2)
    b2 = (G - math.sqrt(2 * G) * K + (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)

    a0 = 1.0
    a1 = (2 * ((K ** 2) - 1)) / (1 + math.sqrt(2) * K + K ** 2)
    a2 = (1 - math.sqrt(2) * K + (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)

    b_list = [b0, b1, b2]
    a_list = [a0, a1, a2]

    # plotting.plot_filter(b_list, a_list, 'High Shelf Filter')

    return sp.signal.lfilter(b_list, a_list, frame_array)


# used for low EQ'ing
def low_shelf_filter(frame_array, gain, freq_cut=200):
    frequency_cutoff = freq_cut
    volume_gain = gain

    K = math.tan(math.pi * frequency_cutoff / evaluator.SAMPLE_RATE)
    G = 10 ** (volume_gain / 20)

    # calculating parameters
    b0 = (1 + math.sqrt(2 * G) * K + G * (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)
    b1 = (2 * (G * (K ** 2) - 1)) / (1 + math.sqrt(2) * K + K ** 2)
    b2 = (1 - math.sqrt(2 * G) * K + G * (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)

    a0 = 1.0
    a1 = (2 * ((K ** 2) - 1)) / (1 + math.sqrt(2) * K + K ** 2)
    a2 = (1 - math.sqrt(2) * K + (K ** 2)) / (1 + math.sqrt(2) * K + K ** 2)

    b_list = [b0, b1, b2]
    a_list = [a0, a1, a2]

    # plotting.plot_filter(b_list, a_list, 'Low Shelf Filter')

    return sp.signal.lfilter(b_list, a_list, frame_array)  # LP


# used for mid EQ'ing
def mid_shelf_filter(frame_array, gain, freq_cut_1=200, freq_cut_2=4500):
    # we will use low & high shelf filters to change mid frequencies
    minus_gain = -gain

    # 1. lower all frequencies with gain level
    frame_array = high_shelf_filter(frame_array, gain, freq_cut=5)

    # 2. boost high & low frequencies back to normal (only mid's have been changed)
    return high_shelf_filter(low_shelf_filter(frame_array, minus_gain, freq_cut=freq_cut_1), minus_gain,
                             freq_cut=freq_cut_2)


def peak_filter(frame_array, gain):
    cutoff_frequency = 1100
    volume_gain = gain
    Q = 10

    K_p = math.tan(math.pi * cutoff_frequency / evaluator.SAMPLE_RATE)
    G_p = 10 ** (volume_gain / 20)

    b0 = (1 + (G_p / Q) * K_p + K_p ** 2) / (1 + (1 / Q) * K_p + K_p ** 2)
    b1 = (2 * ((K_p ** 2) - 1)) / (1 + (1 / Q) * K_p + K_p ** 2)
    b2 = (1 - (G_p / Q) * K_p + K_p ** 2) / (1 + (1 / Q) * K_p + K_p ** 2)

    a0 = 1.0
    a1 = (2 * ((K_p ** 2) - 1)) / (1 + (1 / Q) * K_p + K_p ** 2)
    a2 = (1 - (1 / Q) * K_p + K_p ** 2) / (1 + (1 / Q) * K_p + K_p ** 2)

    b_list = [b0, b1, b2]
    a_list = [a0, a1, a2]

    # plotting.plot_filter(b_list, a_list, 'Peak Filter')

    return sp.signal.lfilter(b_list, a_list, frame_array)


################################################################ utility ################################################################


# replace values that are higher then 1 with 1 and lower then -1 with -1
def reduce_amplitude(frame_array):
    frame_array = np.where(frame_array < -1.0, -1.0, frame_array)
    frame_array = np.where(frame_array > 1.0, 1.0, frame_array)
    return frame_array


def edit_volume_by_factor(audio_channel, factor):
    a_placeholder = []

    for frame in audio_channel:
        a_placeholder.append(frame * factor)

    return np.asarray(a_placeholder, dtype='float32', order='F')


def cut_bass_for_last_bar(list_of_frames, length_of_segment):
    # length_of_segment should be in bars
    length_in_frames = len(list_of_frames)
    frames_to_edit = round(length_in_frames / length_of_segment)
    if frames_to_edit > 100000:
        print("INFO - 1 bar bass cut has propably not the right length... 1 bar frames: '%s', length of segment %s." % (
            frames_to_edit, length_of_segment))
    start = length_in_frames - frames_to_edit

    # print("Removing bass from last bar of segment.")
    # print("start: %s, end: %s" % (start, length_in_frames))

    frames_with_no_bass = []
    for i in range(start, length_in_frames):
        frames_with_no_bass.append(list_of_frames[i])

    frames_with_no_bass = low_cut_filter(frames_with_no_bass, order=3)

    for i in range(frames_to_edit):
        list_of_frames[i + start] = frames_with_no_bass[i]

    return list_of_frames


def modify_mids_and_highs_by_gain(frame_array, gain):
    return mid_shelf_filter(high_shelf_filter(frame_array, gain), gain)
