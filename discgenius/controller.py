import os
import time
import datetime
import io

from . import evaluator
from . import mixer
from . import analysis
from .utility import audio_file_converter as converter
from .utility import utility as util
from .utility import bpm_match
from .utility.model import error_response_model, song_helper

from pymongo.collection import Collection
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket


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


def generate_safe_song_temp_name(config, filename, extension):
    filename = filename.replace("_", "-")
    temp_filename = filename

    # generate safe file ending
    filename = f"{filename}.{extension}"

    # check if file exists
    fwe = temp_filename
    i = 1
    # check if given audio file or audio file in wav already exist, generate new name until a safe one is found
    while os.path.isfile(f"{config['song_analysis_path']}/{filename}") or os.path.isfile(f"{config['song_analysis_path']}/{fwe}.wav"):
        filename = f"{temp_filename}-{i}.{extension}"
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


async def mix_two_files(config,
                  song_a_name,
                  song_b_name,
                  bpm_a,
                  bpm_b,
                  desired_bpm,
                  mix_name,
                  scenario_name,
                  transition_points,
                  entry_point,
                  exit_point,
                  num_songs_a,
                  mix_id,
                  mix_db: Collection,
                  fs: AsyncIOMotorGridFSBucket):
    # check that mongodb mix file exists
    mix_mongo = await mix_db.find_one({"_id": ObjectId(mix_id)})
    if mix_mongo:

        # read the original wav files
        song_a_path = f"{config['song_analysis_path']}/{song_a_name}"
        song_a_data = b""
        song_b_path = f"{config['song_analysis_path']}/{song_b_name}"
        song_b_data = b""
        cursor_a = fs.find({"filename": song_a_name})
        async for grid_data in cursor_a:
            song_a_data = grid_data.read()
        with open(song_a_path, 'wb') as a_f:
            a_f.write(song_a_data)
        # song_a = util.read_wav_file(config, song_a_path, identifier='songA')
        song_a = util.read_wav_file(config, io.BytesIO(song_a_data), identifier='songA')

        cursor_b = fs.find({"filename": song_b_name})
        async for grid_data in cursor_b:
            song_b_data = grid_data.read()
        with open(song_b_path, 'wb') as b_f:
            b_f.write(song_b_data)
        # song_b = util.read_wav_file(config, song_b_path, identifier='songB')
        song_b = util.read_wav_file(config, io.BytesIO(song_a_data), identifier='songB')

        # if num_songs_a > 1:
        #     song_a = util.read_wav_file(config, f"{config['mix_path']}/{song_a_name}", identifier='songA')
        # else:
        #     song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
        # song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')
        # song_a = util.read_wav_file(config, f"{config['song_path']}/{song_a_name}", identifier='songA')
        # song_b = util.read_wav_file(config, f"{config['song_path']}/{song_b_name}", identifier='songB')

        update_data = {
            "progress": 20
        }
        mix_update0 = await mix_db.update_one(
            {"_id": ObjectId(mix_id)},
            {"$set": update_data}
        )
        if not mix_update0:
            print("mix update #0 failed")

        # TSL = Transition Segment Length
        tsl_list = [config['transition_midpoint'], config['transition_length'] - config['transition_midpoint']]

        # 1 match tempo of both songs before analysis
        # TODO write adjusted songs to db
        if desired_bpm != bpm_a:
            song_a_adjusted, song_b_adjusted = bpm_match.match_bpm_desired(config, song_a, song_b, desired_bpm, bpm_a, bpm_b)
        else:
            song_a_adjusted, song_b_adjusted = bpm_match.match_bpm_first(config, song_a, bpm_a, song_b, bpm_b)

        update_data = {
            "progress": 40
        }
        mix_update1 = await mix_db.update_one(
            {"_id": ObjectId(mix_id)},
            {"$set": update_data}
        )
        if not mix_update1:
            print("mix update #1 failed")

        # 2. analyse songs
        if transition_points:
            transition_points['b'] = round(transition_points['a'] + (transition_points['d'] - transition_points['c']), 3)
            transition_points['x'] = round(transition_points['a'] + (transition_points['e'] - transition_points['c']), 3)
        if not transition_points:
            then = time.time()
            transition_points = analysis.get_transition_points(config, song_a_adjusted, song_b_adjusted, exit_point, entry_point, tsl_list)
            now = time.time()
            print("INFO - Analysing file took: %0.1f seconds. \n" % (now - then))

        update_data = {
            "transition_points": transition_points,
            "progress": 60
        }
        mix_update2 = await mix_db.update_one(
            {"_id": ObjectId(mix_id)},
            {"$set": update_data}
        )
        if not mix_update2:
            print("mix update #2 failed")

        print(f"Transition points (seconds): {transition_points}")
        print(f"Transition points (minutes): {util.get_length_for_transition_points(config, transition_points)}")
        print(f"Transition interval lengths (C-D-E): {round(transition_points['d']-transition_points['c'], 3)}s, {round(transition_points['e']-transition_points['d'], 3)}s")
        print(f"Transition interval lengths (A-B-X): {round(transition_points['b']-transition_points['a'], 3)}s, {round(transition_points['x']-transition_points['b'], 3)}s")
        print()

        # 3. mix both songs
        then = time.time()
        frames = util.calculate_frames(config, song_a_adjusted, song_b_adjusted, transition_points)
        # print("Frames: %s" % frames)
        mixed_song = mixer.create_mixed_wav_file(config, song_a_adjusted, song_b_adjusted, transition_points, frames, tsl_list, mix_name, scenario_name)
        now = time.time()
        print("INFO - Mixing file took: %0.1f seconds" % (now - then))

        mix_name_wav = mixed_song['name']
        file_path_wav = mixed_song['path']
        with open(file_path_wav, 'rb') as f:
            grid_in = fs.open_upload_stream(mix_name_wav)
            await grid_in.write(f.read())
            await grid_in.close()
        update_data = {
            "title": mix_name_wav,
            "progress": 80
        }
        mix_update3 = await mix_db.update_one(
            {"_id": ObjectId(mix_id)},
            {"$set": update_data}
        )
        if not mix_update3:
            print("mix update #3 failed")

        # 4. convert to mp3
        if mixed_song:
            mix_name_mp3 = converter.convert_result_to_mp3(config, mixed_song['name'])
            if mix_name_mp3:
                mixed_song['name_mp3'] = mix_name_mp3
                mixed_song['path_mp3'] = f"{config['mix_path']}/{mix_name_mp3}"

        mix_name_mp3 = mixed_song['name_mp3']
        file_path_mp3 = mixed_song['path_mp3']
        with open(file_path_mp3, 'rb') as f:
            grid_in = fs.open_upload_stream(mix_name_mp3)
            await grid_in.write(f.read())
            await grid_in.close()
        update_data = {
            "progress": 100,
            "title_mp3": mix_name_mp3
        }
        mix_update4 = await mix_db.update_one(
            {"_id": ObjectId(mix_id)},
            {"$set": update_data}
        )
        if not mix_update4:
            print("mix update #4 failed")

        # 5. export json data
        scenario_data = util.get_scenario(config, scenario_name)
        scenario_data['short_name'] = scenario_name
        new_num_songs = num_songs_a + 1
        json_data = util.export_transition_parameters_to_json(config, [song_a, song_b, mixed_song], transition_points,
                                                              scenario_data, tsl_list, new_num_songs, desired_bpm)

        os.remove(song_a_path)
        os.remove(song_b_path)
        return json_data
    else:
        return error_response_model("Not Found", 404, f"Mix with id {mix_id} does not exist")

