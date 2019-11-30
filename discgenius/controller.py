import os
import time

from . import evaluator
from . import mixer
from .utility import audio_file_converter as converter
from .utility import utility as util


def generate_safe_filename(config, filename, extension):
    # generate safe file ending
    ending = "wav"
    if len(filename) <= 4:
        filename = f"{filename}.{extension}"
    else:
        ending = filename.split('.')[-1]
    if ending not in config['audio_formats']:
        filename = f"{filename}.{extension}"

    # check if file exists
    filename_without_extension = filename[:-(len(extension) + 1)]
    fwe = filename_without_extension
    i = 1
    while os.path.isfile(f"{config['song_path']}/{filename}") or os.path.isfile(f"{config['song_path']}/{fwe}.wav"):
        filename = f"{filename_without_extension}-{i}.{extension}"
        fwe = filename[:-(len(extension) + 1)]
        i += 1
    return filename


def create_wav_from_mp3(config, filename, extension):
    input_path = f"{config['song_path']}/{filename}"
    output_path = f"{config['song_path']}/{filename[:-(len(extension) + 1)]}.wav"
    converter.convert_mp3_to_wav(config, input_path, output_path)


def mix_two_files(config, song_a_name, song_b_name, mix_name, scenario_name):
    # --- andromeda to 86 --- C-D-E: 5:24-6:24:7:23 --- 32-32

    song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
    song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')

    # 1. analysis songs and change bpm

    # 2. evaluate segments from analysis --> get transition points
    tsl_list, transition_points = evaluator.evaluate_segments(config)

    frames = util.calculate_frames(config, song_a, song_b, transition_points)

    # print("Frames: %s" % frames)
    # print("Transition Points: %s" % transition_points)

    # 3. mix both songs
    then = time.time()
    mixed_song = mixer.create_mixed_wav_file(config, song_a, song_b, transition_points, frames, tsl_list, mix_name)
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now - then))

    # 4. convert to mp3
    if mixed_song:
        mp3_mix_name = converter.convert_result_to_mp3(config, mixed_song['name'])
        if mp3_mix_name:
            os.remove(mixed_song['path'])
            mixed_song['name'] = mp3_mix_name
            mixed_song['path'] = f"{config['mix_path']}/{mp3_mix_name}"

    # 5. export json data
    scenario_data = util.get_scenario(config, scenario_name)
    scenario_data['short_name'] = scenario_name
    json_data = util.export_transition_parameters_to_json(config, [song_a, song_b, mixed_song], transition_points,
                                                          scenario_data, tsl_list)
    return json_data
