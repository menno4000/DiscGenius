import os
from os.path import isfile, join
import uvicorn

from fastapi import FastAPI, HTTPException, Body
from starlette.requests import Request
from starlette.responses import StreamingResponse

from . import controller
from .utility import common, bpmMatch, validator
from .utility import utility as util
from .utility import bpm_detection

app = FastAPI()

config = common.get_config('./content.ini')
SCENARIOS = util.get_scenarios(config, just_names=True)


def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


def save_song(config, filename, song_data):
    with open(f"{config['song_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


def save_temp_song(config, filename, song_data):
    with open(f"{config['song_analysis_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


@app.post("/upload")
async def upload_song(request: Request, filename: str = "", extension: str = "", bpm: str = ""):
    body = await request.body()

    if filename == "" or extension == "":
        raise_exception(400, "Please provide a filename and the extension (format) of the song as query parameters.")
    if not body:
        raise_exception(400, "Please provide an audio file as a binary file.")
    if extension not in config['audio_formats']:
        raise_exception(400, "Audio format not supported. Please provide one of the following formats: %s" % config[
            'audio_formats'])
    # create temp file to run bpm detection on
    temp_filename = controller.generate_safe_song_temp_name(config, filename, extension)
    save_temp_song(config, temp_filename, body)

    if bpm == "":
        bpm = bpm_detection.estimate_tempo(config, temp_filename, 3)

    bpm = validator.convert_bpm(config, bpm)

    filename = controller.generate_safe_song_name(config, filename, extension, bpm)
    save_song(config, filename, body)

    # remove bpm detection temp files
    os.remove(f"{config['song_analysis_path']}/{temp_filename}")

    if not extension == "wav":
        controller.create_wav_from_audio(config, filename, extension)

        filename = filename[:-(len(extension))] + "wav"
        return {
            "filename": filename,
            "info": "'.wav file' was created. Please refer to this file when calling /createMix."
        }
    return {
        "filename": filename,
        "info": "Please refer to this name, when calling '/createMix'"
    }

@app.post("/extendMix")
async def extendMix(mix_a_name: str = Body(default=""), song_b_name: str = Body(default=""),
                    mix_name: str = Body(default=""),
                    scenario_name: str = Body(default="EQ_1.0"),
                    bpm: float = Body(default=0),
                    transition_length: int = Body(default=32),
                    transition_midpoint: int = Body(default=16),
                    transition_points: dict = Body(default=None),
                    entry_point: float = Body(default=config['mix_area'])):
    if mix_a_name == "" or song_b_name == "" or scenario_name == "":
        raise_exception(status_code=422, detail=util.read_api_detail(config))

    if not os.path.isfile(f"{config['mix_path']}/{mix_a_name}") or not os.path.isfile(
            f"{config['song_path']}/{song_b_name}"):
        raise_exception(404, "One of the two given songs could not be found. "
                             "Please check using GET '/songs' which songs exist.")

    # TODO retrieve number of included songs from song description json
    num_songs_a, bpm_a = util.read_mix_content_data(config, mix_a_name)
    if bpm == 0:
        desired_bpm = bpm_a
    else:
        desired_bpm = bpm


    if scenario_name not in SCENARIOS:
        raise_exception(422, "Transition scenario could not be found.")

    exit_point_modifier = entry_point / num_songs_a
    exit_point = 1 - exit_point_modifier


    if exit_point < 0.0 or exit_point > 1.0 or entry_point < 0.0 or entry_point > 1.0:
        raise_exception(422, "exit_point or entry_point must be floating point numbers between 0 and 1.")

    bpm_a, bpm_b, desired_bpm = validator.validate_bpms_extend(config, song_b_name, bpm_a, desired_bpm)

    transition_length, transition_midpoint, transition_points = validator.validate_transition_times(config, transition_length, transition_midpoint, transition_points, desired_bpm, mix_a_name, song_b_name)
    config['transition_length'] = transition_length
    config['transition_midpoint'] = transition_midpoint

    mix_name = controller.generate_safe_mix_name(config, mix_name, desired_bpm, scenario_name)

    print(f"INFO - A new mix will get created from songs '{mix_a_name}' & '{song_b_name}'.")
    print(f"       Transition length: {transition_length}, Transition midpoint: {transition_midpoint}, Desired bpm: '{desired_bpm}'.")
    print(f"       Mix name: '{mix_name}'.")
    print()

    return controller.mix_two_files(config, mix_a_name, song_b_name, bpm_a, bpm_b, desired_bpm, mix_name, scenario_name, transition_points, entry_point, exit_point, num_songs_a)


@app.post("/createMix")
async def mix(song_a_name: str = Body(default=""), song_b_name: str = Body(default=""),
              mix_name: str = Body(default=""),
              scenario_name: str = Body(default="EQ_1.0"),
              bpm: float = Body(default=0),
              transition_length: int = Body(default=32),
              transition_midpoint: int = Body(default=16),
              transition_points: dict = Body(default=None),
              entry_point: float = Body(default=config['mix_area'])):
    if song_a_name == "" or song_b_name == "" or scenario_name == "":
        raise_exception(status_code=422, detail=util.read_api_detail(config))

    if not os.path.isfile(f"{config['song_path']}/{song_a_name}") or not os.path.isfile(
            f"{config['song_path']}/{song_b_name}"):
        raise_exception(404, "One of the two given songs could not be found. "
                             "Please check using GET '/songs' which songs exist.")

    num_songs_a = 1

    if scenario_name not in SCENARIOS:
        raise_exception(422, "Transition scenario could not be found.")

    exit_point = 1 - entry_point
    if exit_point < 0.0 or exit_point > 1.0 or entry_point < 0.0 or entry_point > 1.0:
        raise_exception(422, "exit_point or entry_point must be floating point numbers between 0 and 1.")

    bpm_a, bpm_b, desired_bpm = validator.validate_bpms_create(config, song_a_name, song_b_name, bpm)

    transition_length, transition_midpoint, transition_points = validator.validate_transition_times(config, transition_length, transition_midpoint, transition_points, desired_bpm, song_a_name, song_b_name)
    config['transition_length'] = transition_length
    config['transition_midpoint'] = transition_midpoint

    mix_name = controller.generate_safe_mix_name(config, mix_name, desired_bpm, scenario_name)

    print(f"INFO - A new mix will get created from songs '{song_a_name}' & '{song_b_name}'.")
    print(f"       Transition length: {transition_length}, Transition midpoint: {transition_midpoint}, Desired bpm: '{desired_bpm}'.")
    print(f"       Mix name: '{mix_name}'.")
    print()

    return controller.mix_two_files(config, song_a_name, song_b_name, bpm_a, bpm_b, desired_bpm, mix_name, scenario_name, transition_points, entry_point, exit_point, num_songs_a)


@app.post("/adjustTempo")
async def adjust_tempo(song_name: str = Body(default=""),
                       bpm: float = Body(default=0.0)):
    if song_name == "" or bpm == 0:
        raise_exception(422, "Please provide two attributes in JSON: 'song_name' and 'bpm'")

    if not os.path.isfile(f"{config['song_path']}/{song_name}"):
        raise_exception(404, "The given song could not be found. "
                             "Please check using GET '/songs' which songs exist.")

    old_bpm = validator.convert_bpm(config, util.get_bpm_from_filename(song_name))
    desired_bpm = validator.convert_bpm(config, bpm)

    song_name = ''.join(song_name.split('_')[:-1])
    new_song_name = bpmMatch.adjust_tempo(config, song_name, old_bpm, desired_bpm)

    return {
        "filename": new_song_name,
        "info": f"A copy of the original song was created in a new tempo ({desired_bpm}). Please refer to this name, when calling '/createMix'"
    }


@app.get("/getMix")
async def get_mix(name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")

    mix_path = f"{config['mix_path']}/{name}"
    if not os.path.isfile(mix_path):
        raise HTTPException(status_code=404, detail="Mix not found. Please check under GET '/mixes' which mixes exist.")

    mix = open(mix_path, 'rb')
    response = StreamingResponse(mix, media_type='audio/mpeg')
    return response


@app.get("/songs")
async def get_songs():
    return [f for f in os.listdir(config['song_path']) if isfile(join(config['song_path'], f)) and '.wav' in f]


@app.get("/mixes")
async def get_mixes():
    return [f for f in os.listdir(config['mix_path']) if isfile(join(config['mix_path'], f)) and '.mp3' in f]


@app.get("/scenarios")
async def get_scenarios():
    return util.get_scenarios(config, just_names=False)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9001, log_level='debug')
