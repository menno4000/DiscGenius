import librosa
import soundfile as sf

def match_bpm_first(song_a, tempo_a, song_b, tempo_b):
    tempo_ratio = tempo_a / tempo_b
    rate_b = song_b.frame_rate
    new_rate_b = rate_b / tempo_ratio

    print("INFO - Matching tempo of song "+song_b.name+" ("+str(tempo_b)+") to tempo of song "+song_a.name+" ("+str(tempo_a)+")")
    song_b_resampled = librosa.resample(song_b.frames, rate_b, new_rate_b)
    song_b['frames'] = song_b_resampled[0]
    song_b['left_channel'] = song_b_resampled[0][0]
    song_b['right_channel'] = song_b_resampled[0][1]

def match_bpm_desired(song_a, tempo_a, song_b, tempo_b, desired_tempo):
    tempo_ratio_a = desired_tempo / tempo_a
    rate_a = song_b.frame_rate
    new_rate_a = rate_a / tempo_ratio_a

    print("INFO - Matching tempos of song "+song_a.name+" ("+str(tempo_a)+") to desired tempo "+str(desired_tempo))
    song_a_resampled = librosa.resample(song_a.frames, rate_a, new_rate_a)
    song_a['frames'] = song_a_resampled[0]
    song_a['left_channel'] = song_a_resampled[0][0]
    song_a['right_channel'] = song_a_resampled[0][1]

    tempo_ratio_b = desired_tempo / tempo_b
    rate_b = song_b.frame_rate
    new_rate_b = rate_b / tempo_ratio_b

    print("INFO - Matching tempos of song "+song_b.name+" ("+str(tempo_b)+") to desired tempo "+str(desired_tempo))
    song_b_resampled = librosa.resample(song_b.frames, rate_b, new_rate_b)
    song_b['frames'] = song_b_resampled[0]
    song_b['left_channel'] = song_b_resampled[0][0]
    song_b['right_channel'] = song_b_resampled[0][1]
