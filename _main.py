import time

import evaluator
import mixer
import utility as util
import audio_file_converter as converter

if __name__ == '__main__':

    # 1. convert wav to mp3
    # converter.convert_mp3_to_wav("../AudioExampleFiles/Spirit Architect - Morning Glory.mp3", "../AudioExampleFiles/Spirit Architect - Morning Glory.wav")
    # converter.convert_mp3_to_wav("../AudioExampleFiles/Spirit Architect - Moonshine - 01 Ayahuasca.mp3", "../AudioExampleFiles/Spirit Architect - Moonshine - 01 Ayahuasca.wav")

    #	--- morning glory to ayahuasca --- C-D-E: 5:04-5:57-6:50 --- 32-32

    paths = {'song_a_path': "../AudioExampleFiles/Spirit Architect - Morning Glory.wav",
             'song_b_path': "../AudioExampleFiles/Spirit Architect - Moonshine - 01 Ayahuasca.wav"
             }

    song_a = util.read_wav_file(paths['song_a_path'])
    song_b = util.read_wav_file(paths['song_b_path'])

    # 2. analysis songs and change bpm


    # 3. evaluate segments from analysis --> get transition points
    tsl_list, transition_points = evaluator.evaluate_segments()
    paths['result_path'] = "../AudioExampleFiles/Mixes/" + "morning_glory_to_ayahuasca_" + str(transition_points['a']) + ".wav"

    frames = util.calculate_frames(song_a, song_b, transition_points)

    print("Frames: %s" % frames)
    print("Transition Points: %s" % transition_points)


    # 4. mix both songs
    then = time.time()
    mixed_song = mixer.create_mixed_wav_file(song_a, song_b, transition_points, paths, frames, tsl_list)
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now - then))


    # 5. save mixed file and convert to mp3
    util.save_wav_file(mixed_song, paths['result_path'])
    converter.convert_result_to_mp3(paths['result_path'], 128)