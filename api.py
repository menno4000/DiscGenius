import os
from os.path import isfile, join

import controller
import utility as util
from fastapi import FastAPI, HTTPException, Body
from starlette.requests import Request
from starlette.responses import StreamingResponse

app = FastAPI()

config = util.get_config()
SCENARIOS = util.get_scenarios(config, just_names=True)


def generate_safe_filename(filename, extension):
    # generate safe file ending
    ending = ""
    if len(filename) <= 4:
        filename = f"{filename}.{extension}"
    else:
        ending = filename.split('.')[-1]
    if not ending == extension:
        filename = f"{filename}.{extension}"

    # check if file exists
    filename_without_extension = filename[:-(len(extension) + 1)]
    i = 1
    while os.path.isfile(f"{config['song_path']}/{filename}"):
        filename = f"{filename_without_extension}-{i}.{extension}"
        i += 1
    return filename


def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


def save_song(config, filename, song_data):
    with open(f"{config['song_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


@app.post("/mix")
async def mix(song_a_name: str = Body(default=""), song_b_name: str = Body(default=""), mix_name: str = Body(default=""),
              scenario_name: str = Body(default="")):
    if song_a_name == "" or song_b_name == "" or scenario_name == "":
        raise_exception(400, "Please provide three attributes: 'song_a_name', 'song_b_name' and 'transition_scenario'.")

    if not os.path.isfile(f"{config['song_path']}/{song_a_name}") or not os.path.isfile(
            f"{config['song_path']}/{song_b_name}"):
        raise_exception(404, "One of the two given songs could not be found. "
                             "Please check under 'GET /songs' which songs exist.")

    if scenario_name not in SCENARIOS:
        raise_exception(400, "Transition scenario could not be found.")

    return controller.mix_two_files(config, song_a_name, song_b_name, mix_name, scenario_name)


@app.post("/upload")
async def upload_song(filename: str, extension: str, request: Request):
    body = await request.body()
    filename = generate_safe_filename(filename, extension)

    save_song(config, filename, body)

    # todo if mp3 start thread to convert file to wav
    return {
        "filename": filename,
        "info": "Please refer to this name, when calling '/mix'"
    }


@app.get("/getMix")
async def get_mix(name_of_mix: str = ""):
    if name_of_mix == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")

    mix_path = f"{config['mix_path']}/{name_of_mix}"
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
