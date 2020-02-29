import os
import time

from . import evaluator
from . import mixer
from . import analysis
from .utility import audio_file_converter as converter
from .utility import utility as util
from .utility import bpmMatch


def generate_safe_song_name(config, filename, extension, bpm):
    filename = filename.replace("_", "-")

    # generate safe file ending
    filename = f"{filename}_{bpm}.{extension}"

    # check if file exists
    filename_without_extension_and_bpm = filename.split('_')[0]
    fwe = filename_without_extension_and_bpm
    i = 1
    # check if given audio file or audio file in wav already exist, generate new name until a safe one is found
    while os.path.isfile(f"{config['song_path']}/{filename}") or os.path.isfile(f"{config['song_path']}/{fwe}.wav"):
        filename = f"{filename_without_extension_and_bpm}-{i}_{bpm}.{extension}"
        fwe = filename[:-(len(extension) + 1)]
        i += 1
    return filename


def generate_safe_mix_name(config, orig_filename, bpm):
    i = 1
    new_filename = f"{orig_filename}_{bpm}"
    while os.path.isfile(f"{config['mix_path']}/{new_filename}.wav") or os.path.isfile(f"{config['mix_path']}/{new_filename}.mp3"):
        new_filename = f"{orig_filename}-{i}_{bpm}"
        i += 1
    return new_filename


def create_wav_from_audio(config, filename, extension):
    input_path = f"{config['song_path']}/{filename}"
    output_path = f"{config['song_path']}/{filename[:-(len(extension) + 1)]}.wav"
    converter.convert_audio_to_wav(config, input_path, output_path)
    util.move_audio_to_storage(config, input_path)


def mix_two_files(config, song_a_name, song_b_name, song_a_bpm, song_b_bpm, mix_name, scenario_name, bpm=0, transition_length=8):
    # --- andromeda to 86 --- C-D-E: 5:24-6:24:7:23 --- 32-32

    # read the original wav files
    song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
    song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')

    # 1.1 match tempo of both songs before analysis
    # if no bpm is provided, match tempo of song_b to song_a
    if bpm == 0:
        song_a, song_b = bpmMatch.match_bpm_first(config, song_a, song_a_bpm, song_b, song_b_bpm)
    else:
        song_a, song_b = bpmMatch.match_bpm_desired(config, song_a, song_a_bpm, song_b, song_b_bpm, bpm)
    # 1.2 analyse songs
    transition_points = analysis.get_transition_points(config, song_a, song_b, transition_length)

    # 2. evaluate segments from analysis --> get transition points
    tsl_list, transition_points = evaluator.evaluate_segments(config, transition_points, transition_length)

    frames = util.calculate_frames(config, song_a, song_b, transition_points)

    # print("Frames: %s" % frames)
    print("Transition Points: %s" % transition_points)

    # 3. mix both songs
    then = time.time()
    mixed_song = mixer.create_mixed_wav_file(config, song_a, song_b, transition_points, frames, tsl_list, mix_name, scenario_name)
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now - then))

    # 4. convert to mp3
    if mixed_song:
        mp3_mix_name = converter.convert_result_to_mp3(config, mixed_song['name'])
        if mp3_mix_name:
            #os.remove(mixed_song['path'])
            mixed_song['name'] = mp3_mix_name
            mixed_song['path'] = f"{config['mix_path']}/{mp3_mix_name}"

    # 5. export json data
    scenario_data = util.get_scenario(config, scenario_name)
    scenario_data['short_name'] = scenario_name
    json_data = util.export_transition_parameters_to_json(config, [song_a, song_b, mixed_song], transition_points,
                                                          scenario_data, tsl_list)
    return json_data
