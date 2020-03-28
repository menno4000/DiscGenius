import numpy
import aubio
import librosa


def aubio_beats_to_bpm(beats):
    # if enough beats are found, convert to periods then to bpm
    if len(beats) > 1:
        if len(beats) < 4:
            print("few beats found.")
        bpms = 60./numpy.diff(beats)
        return numpy.median(bpms)
    else:
        print("not enough beats found")
        return 0


def aubio_beat_tracking(filepath, sample_rate, win_s=512):
    win_s = win_s               # fft size
    hop_s = win_s // 2          # hop size
    src = aubio.source(filepath, hop_size=hop_s)
    #print(f"file: {src.uri}, samplerate: {src.samplerate}, channels: {src.channels}, duration: {src.duration/src.samplerate}")

    o = aubio.tempo("default", win_s, hop_s, sample_rate)

    # tempo detection delay, in samples
    # default to 4 blocks delay to catch up with
    delay = 4. * hop_s

    # list of beats, in samples
    beats = []

    # total number of frames read
    total_frames = 0
    while True:
        samples, read = src()
        is_beat = o(samples)
        if is_beat:
            this_beat = int(total_frames - delay + is_beat[0] * hop_s)
            #print("%f" % (this_beat / float(SAMPLE_RATE)))
            beats.append(this_beat/sample_rate)
        total_frames += read
        if read < hop_s: break

    return beats, aubio_beats_to_bpm(beats)


def librosa_beat_tracking(signal, sample_rate):
    # compute onset envelopes
    onset_env = librosa.onset.onset_strength(y=signal, sr=sample_rate, aggregate=numpy.median)

    # compute beats using librosa beat tracking
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sample_rate)

    # create onset sample matrix from tracked beats
    onset_samples = list(librosa.frames_to_samples(beats))
    onset_samples = numpy.concatenate(onset_samples, len(signal))

    # derive frame index of beat starts/stops from onset sample matrix
    starts = onset_samples[0:-1]
    stops = onset_samples[1:]

    times_starts = librosa.samples_to_time(starts, sr=sample_rate)
    times_stops = librosa.samples_to_time(stops, sr=sample_rate)

    #print(f"len of beats: {len(beats)}")
    #print(f"len of onset_samples: {len(onset_samples)}")
    #print(f"len of starts: {len(starts)}")
    #print(f"len of stops: {len(stops)}")
    #print(f"len of times_starts: {len(times_starts)}")
    #print(f"len of times_stops: {len(times_stops)}")
    #print(f"beats: {beats[:10]}")
    #print(f"onset_samples: {onset_samples[:10]}")
    #print(f"starts: {starts[:10]}")
    #print(f"stops: {stops[:10]}")
    #print(f"times_starts: {times_starts[:10]}")
    #print(f"times_stops: {times_stops[:10]}")

    return times_starts, times_stops


