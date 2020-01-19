import librosa
import soundfile as sf

#setup signals to be matched with each other
#remove this once the method is plugged in to the application
song_1 = "./oblivion.wav"
song_2 = "./boomblast.wav"
signal_1, rate_1 = librosa.load(song_1)
signal_2, rate_2 = librosa.load(song_2)

print(signal_1, rate_1, signal_2, rate_2)

#method for matching the tempo of two signals
#when tempo needs to be changed for both songs, use desired_tempo parameter
#when desired_tempo equals 0, signal_2 tempo is matched to signal_1
#return the changed signals. reuse the inputted rates for playback

def matchTimes(signal_1, signal_2, rate_1, rate_2, desired_tempo=0):
    tempo_1, beats_1 = librosa.beat.beat_track(y=signal_1, sr=rate_1)
    tempo_2, beats_2 = librosa.beat.beat_track(y=signal_2, sr=rate_2)

    if desired_tempo == 0:
        print("matching second signal to first signal. Tempo 1: "+str(tempo_1)+" Tempo 2: "+str(tempo_2)+" Desired Tempo: "+str(tempo_1))
        tempo_ratio = tempo_1 / tempo_2
        print("tempo ratio: "+str(tempo_ratio))
        new_rate_2 = (rate_2/tempo_ratio)
        signal_2_stretched = librosa.resample(signal_2, rate_2, new_rate_2)

        return(signal_1, signal_2_stretched, 0, tempo_ratio)

    else:
        print("matching signals to desired tempo. Tempo 1: "+str(tempo_1)+" Tempo 2: "+str(tempo_2)+" Desired Tempo: "+str(desired_tempo))
        tempo_ratio_1 = desired_tempo/tempo_1
        tempo_ratio_2 = desired_tempo/tempo_2
        print("tempo ratio 1: "+str(tempo_ratio_1))
        print("tempo ratio 2: "+str(tempo_ratio_2))

        new_rate_1 = (rate_1/tempo_ratio_1)
        new_rate_2 = (rate_2/tempo_ratio_2)

        signal_1_stretched = librosa.resample(signal_1, rate_1, new_rate_1)
        signal_2_stretched = librosa.resample(signal_2, rate_2, new_rate_2)

        return(signal_1_stretched, signal_2_stretched, tempo_ratio_1, tempo_ratio_2)

signal_1, signal_2_stretched = matchTimes(signal_1, signal_2, rate_1, rate_2)
sf.write("boomblast_01.wav", signal_2_stretched, rate_2)
sf.write("oblivion_01.wav", signal_1, rate_1)

signal_1_stretched, signal_2_stretched = matchTimes(signal_1, signal_2, rate_1, rate_2, desired_tempo=130.0)
sf.write("boomblast_02.wav", signal_2_stretched, rate_2)
sf.write("oblivion_02.wav", signal_1_stretched, rate_1)
