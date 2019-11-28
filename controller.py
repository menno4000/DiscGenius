import os
import time

import utility as util
import evaluator
import mixer
import audio_file_converter as converter


def mix_two_files(config, song_a_name, song_b_name, mix_name, scenario_name):
    # 1. convert mp3 to wav
    # converter.convert_mp3_to_wav("../AudioExampleFiles/Spirit Architect - Morning Glory.mp3", "../AudioExampleFiles/Spirit Architect - Morning Glory.wav")
    # converter.convert_mp3_to_wav("../AudioExampleFiles/Spirit Architect - Moonshine - 01 Ayahuasca.mp3", "../AudioExampleFiles/Spirit Architect - Moonshine - 01 Ayahuasca.wav")

    # --- andromeda to 86 --- C-D-E: 5:24-6:24:7:23 --- 32-32

    song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
    song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')

    # 2. analysis songs and change bpm

    # 3. evaluate segments from analysis --> get transition points
    tsl_list, transition_points = evaluator.evaluate_segments(config)

    frames = util.calculate_frames(config, song_a, song_b, transition_points)

    # print("Frames: %s" % frames)
    # print("Transition Points: %s" % transition_points)

    # 4. mix both songs
    then = time.time()
    mixed_song = mixer.create_mixed_wav_file(config, song_a, song_b, transition_points, frames, tsl_list, mix_name)
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now - then))

    # 5. convert to mp3
    if mixed_song:
        mp3_mix_name = converter.convert_result_to_mp3(config, mixed_song['name'])
        if mp3_mix_name:
            os.remove(mixed_song['path'])
            mixed_song['name'] = mp3_mix_name
            mixed_song['path'] = f"{config['mix_path']}/{mp3_mix_name}"

    # 6. export json data
    scenario_data = util.get_scenario(config, scenario_name)
    scenario_data['short_name'] = scenario_name
    json_data = util.export_transition_parameters_to_json(config, [song_a, song_b, mixed_song], transition_points,
                                                          scenario_data, tsl_list)
    return json_data


if __name__ == '__main__':
    config = util.get_config()
    song_a_name = "Sisko Electrofanatik - Onium (Original Mix).wav"
    song_b_name = "Hell Driver - Shorebreak (Original Mix).wav"
    mix_two_files(config, song_a_name, song_b_name, "", "EQ_1")
