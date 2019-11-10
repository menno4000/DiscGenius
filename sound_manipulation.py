from scipy.signal import butter, lfilter
import numpy as np
import evaluator


def high_cut(order=5):
    type = 'low'
    cutoff = 2000

    nyq = 0.5 * evaluator.SAMPLE_RATE
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=type, analog=False)
    return b, a


def high_cut_filter(data, order=5):
    b, a = high_cut(order=order)
    frames = lfilter(b, a, data)
    return frames.astype('float32')


def low_cut(order=5):
    type = 'high'
    cutoff = 200

    nyq = 0.5 * evaluator.SAMPLE_RATE
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=type, analog=False)
    return b, a


def low_cut_filter(data, order=5):
    b, a = low_cut(order=order)
    frames = lfilter(b, a, data)
    return frames.astype('float32')


def bandstop(order=5):
    type = 'bandstop'
    freq_values = [200, 2000]
    b, a = butter(order, freq_values, btype=type, analog=False)
    return b, a


def bandstop_filter(data, order):
    b, a = bandstop(order=order)
    frames = lfilter(b, a, data)
    return frames


def cut_bass_for_last_bar(list_of_frames, length_of_segment):
    # length of segment should be in bars
    length_in_frames = len(list_of_frames)
    frames_to_edit = round(length_in_frames/length_of_segment)
    start = length_in_frames-frames_to_edit
    #print("Removing bass from last bar of segment.")
    #print("start: %s, end: %s" % (start, length_in_frames))

    frames_with_no_bass = []
    for i in range(start, length_in_frames):
        frames_with_no_bass.append(list_of_frames[i])

    frames_with_no_bass = low_cut_filter(frames_with_no_bass, order=3)

    for i in range(frames_to_edit):
        list_of_frames[i+start] = frames_with_no_bass[i]

    return list_of_frames


def edit_volume_by_factor(audio_channel, factor):
    a_placeholder = []

    for frame in audio_channel:
        a_placeholder.append(frame * factor)

    return np.asarray(a_placeholder, dtype='float32', order='F')


# replace values that are higher then 1 with 1 and lower then -1 with -1
def reduce_amplitude(frame_array):
    frame_array = np.where(frame_array < -1.0, -1.0, frame_array)
    frame_array = np.where(frame_array > 1.0, 1.0, frame_array)
    return frame_array

