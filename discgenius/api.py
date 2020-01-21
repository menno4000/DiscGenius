import os
from os.path import isfile, join

from fastapi import FastAPI, HTTPException, Body
from starlette.requests import Request
from starlette.responses import StreamingResponse

from . import controller
from .utility import common
from .utility import utility as util

app = FastAPI()

config = common.get_config('./content.ini')
SCENARIOS = util.get_scenarios(config, just_names=True)


def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


def save_song(config, filename, song_data):
    with open(f"{config['song_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


def convert_bpm(bpm):
    try:
        return float(bpm)
    except ValueError:
        raise_exception(400, "Please provide a number as bpm value.")


@app.post("/upload")
async def upload_song(request: Request, filename: str = "", extension: str = "", bpm: str = ""):
    body = await request.body()

    if filename == "" or extension == "" or bpm == "":
        raise_exception(400, "Please provide a filename, the extension (format) of the file and the bpm value of the song as query parameters.")
    if not body:
        raise_exception(400, "Please provide an audio file as a binary file.")
    if extension not in config['audio_formats']:
        raise_exception(400, "Audio format not supported. Please provide one of the following formats: %s" % config[
            'audio_formats'])

    bpm = convert_bpm(bpm)

    filename = controller.generate_safe_song_name(config, filename, extension, bpm)
    save_song(config, filename, body)

    if not extension == "wav":
        controller.create_wav_from_mp3(config, filename, extension)
        filename = filename[:-(len(extension))] + "wav"
        return {
            "filename": filename,
            "info": "'.wav file' was created. Please refer to this file when calling /createMix."
        }
    return {
        "filename": filename,
        "info": "Please refer to this name, when calling '/createMix'"
    }


@app.post("/createMix")
async def mix(song_a_name: str = Body(default=""), song_b_name: str = Body(default=""),
              mix_name: str = Body(default=""),
              scenario_name: str = Body(default=""),
              bpm: str = Body(default="")):
    if song_a_name == "" or song_b_name == "" or scenario_name == "" or bpm == "":
        raise_exception(400, "Please provide four attributes: 'song_a_name', 'song_b_name', 'scenario_name' and 'bpm'.")

    if not os.path.isfile(f"{config['song_path']}/{song_a_name}") or not os.path.isfile(
            f"{config['song_path']}/{song_b_name}"):
        raise_exception(404, "One of the two given songs could not be found. "
                             "Please check under 'GET /songs' which songs exist.")

    if scenario_name not in SCENARIOS:
        raise_exception(400, "Transition scenario could not be found.")

    bpm = convert_bpm(bpm)

    mix_name = controller.generate_safe_mix_name(config, mix_name, bpm)
    return controller.mix_two_files(config, song_a_name, song_b_name, mix_name, scenario_name, bpm)


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
