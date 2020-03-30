import os
import time
import datetime

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


def generate_safe_mix_name(config, orig_filename, bpm, scenario_name):
    if orig_filename == "":
        orig_filename = f"mix_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"

    i = 1
    segment_length_a = config['transition_midpoint']
    segment_length_b = config['transition_length'] - segment_length_a
    new_filename = f"{orig_filename}_{bpm}_{scenario_name}_{segment_length_a}-{segment_length_b}"
    while os.path.isfile(f"{config['mix_path']}/{new_filename}.wav") or os.path.isfile(f"{config['mix_path']}/{new_filename}.mp3"):
        new_filename = f"{orig_filename}-{i}_{bpm}_{scenario_name}_{segment_length_a}-{segment_length_b}"
        i += 1
    return new_filename


def create_wav_from_audio(config, filename, extension):
    input_path = f"{config['song_path']}/{filename}"
    output_path = f"{config['song_path']}/{filename[:-(len(extension) + 1)]}.wav"
    converter.convert_audio_to_wav(config, input_path, output_path)
    util.move_audio_to_storage(config, input_path)


def mix_two_files(config, song_a_name, song_b_name, bpm_a, bpm_b, desired_bpm, mix_name, scenario_name, transition_length=16, transition_midpoint=8):
    # read the original wav files
    song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
    song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')

    config['transition_length'] = transition_length
    config['transition_midpoint'] = transition_midpoint

    print(f"INFO - A new mix will get created from songs '{song_a_name}' & '{song_b_name}'.")
    print(f"       Transition length: {transition_length}, Transition midpoint: {transition_midpoint}, Desired bpm: '{desired_bpm}'.")
    print(f"       Mix name: '{mix_name}'.")
    print()

    # 1.1 match tempo of both songs before analysis
    song_a_adjusted, song_b_adjusted = bpmMatch.match_bpm_desired(config, song_a, song_b, desired_bpm, bpm_a, bpm_b)

    # 1.2 analyse songs
    then = time.time()
    transition_points = analysis.get_transition_points(config, song_a_adjusted, song_b_adjusted)
    now = time.time()
    print("INFO - Analysing file took: %0.1f seconds. \n" % (now - then))

    # 2. evaluate segments from analysis --> get transition points
    tsl_list, transition_points = evaluator.evaluate_segments(config, transition_points)

    frames = util.calculate_frames(config, song_a_adjusted, song_b_adjusted, transition_points)

    # print("Frames: %s" % frames)
    print(f"Transition points (seconds): {transition_points}")
    print(f"Transition points (minutes): {util.get_length_for_transition_points(config, transition_points)}")
    print(f"Transition interval lengths (C-D-E): {transition_points['d']-transition_points['c']}, {transition_points['e']-transition_points['d']}")
    print(f"Transition interval lengths (A-B-X): {transition_points['b']-transition_points['a']}, {transition_points['x']-transition_points['b']}")
    print()

    # 3. mix both songs
    then = time.time()
    mixed_song = mixer.create_mixed_wav_file(config, song_a_adjusted, song_b_adjusted, transition_points, frames, tsl_list, mix_name, scenario_name)
    now = time.time()
    print("INFO - Mixing file took: %0.1f seconds" % (now - then))

    # 4. convert to mp3
    #if mixed_song:
    #    mp3_mix_name = converter.convert_result_to_mp3(config, mixed_song['name'])
    #    if mp3_mix_name:
    #        #os.remove(mixed_song['path'])
    #        mixed_song['name'] = mp3_mix_name
    #        mixed_song['path'] = f"{config['mix_path']}/{mp3_mix_name}"

    # 5. export json data
    scenario_data = util.get_scenario(config, scenario_name)
    scenario_data['short_name'] = scenario_name
    json_data = util.export_transition_parameters_to_json(config, [song_a, song_b, mixed_song], transition_points,
                                                          scenario_data, tsl_list)
    return json_data
