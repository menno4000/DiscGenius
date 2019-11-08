from scipy.signal import butter, lfilter
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