import os
from os.path import isfile, join

from fastapi import FastAPI, HTTPException, Body
from starlette.requests import Request
from starlette.responses import StreamingResponse

from . import controller, evaluator
from .utility import common, bpmMatch
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
    if bpm == 0.0:
        return bpm
    try:
        bpm = float(bpm)
        if bpm < config['min_bpm'] or bpm > config['max_bpm']:
            raise_exception(400, f"Please set a bpm value between {config['min_bpm']} and {config['max_bpm']}.")
        return bpm

    except ValueError:
        raise_exception(400, "Please provide a float-number as bpm value.")


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


@app.post("/createMix")
async def mix(song_a_name: str = Body(default=""), song_b_name: str = Body(default=""),
              mix_name: str = Body(default=""),
              scenario_name: str = Body(default="EQ_1.0"),
              bpm: float = Body(default=0),
              transition_length: int = Body(default=32),
              transition_midpoint: int = Body(default=-1337)):
    if song_a_name == "" or song_b_name == "" or scenario_name == "":
        raise_exception(
            status_code=422,
            detail="Please provide four attributes in JSON: 'song_a_name', 'song_b_name', 'song_a_bpm', 'song_a_bpm' \n "
                   "Optionally Provide mix_name (str), scenario_name (str default EQ_1.1, see below), transition_length (int default 16), midpoint (int default 8)"
                   "Example Body:"
                   "{   "
                   "   \"song_a_name\": \"<song_name_1>_120.185.wav\","
                   "   \"song_b_name\": \"<song_name_2>_120.185.wav\","
                   "   \"mix_name\": \"<song_name_1>_to_<song_name_2>\","
                   "   \"scenario_name\": \"EQ_1.0\","
                   "   \"bpm\": \"127,5\","
                   "   \"transition_length\": \"32\","
                   "   \"transition_midpoin\": \"16\""
                   "}"
                   "available scenarios:"
                   "CF_1.0  crossfade with configurable vff values"
                   "EQ_1.0  smooth 3-band-EQ transition with bass swap"
                   "EQ_1.1  smooth 3-band-EQ transition with bass swap and 1 bar bass cut"
                   "EQ_2.0  'hard' 3-band-EQ transition with bass swap"
                   "EQ_2.1  'hard' 3-band-EQ transition with bass swap and 1 bar bass cut"
                   "VFF_1.0 volume fading transition"
                   "VFF_1.1 volume fading transition and 1 bar bass cut")

    if not os.path.isfile(f"{config['song_path']}/{song_a_name}") or not os.path.isfile(
            f"{config['song_path']}/{song_b_name}"):
        raise_exception(404, "One of the two given songs could not be found. "
                             "Please check using GET '/songs' which songs exist.")

    if scenario_name not in SCENARIOS:
        raise_exception(422, "Transition scenario could not be found.")

    if transition_length < 2:
        raise_exception(400, "Transition length should be greater then one.")
    if transition_midpoint == 1337:
        transition_midpoint = transition_length / 2
    if transition_midpoint > transition_length or transition_midpoint < 0:
        raise_exception(400,
                        f"Transition midpoint should be between zero and given transition length ({transition_length}).")

    config['transition_midpoint'] = transition_midpoint
    config['transition_length'] = transition_length

    bpm_a = convert_bpm(util.get_bpm_from_filename(song_a_name))
    bpm_b = convert_bpm(util.get_bpm_from_filename(song_b_name))
    desired_bpm = convert_bpm(bpm)
    if desired_bpm == 0.0:
        desired_bpm = bpm_a

    if abs(bpm_a - bpm_b) > config['max_bpm_diff']:
        raise_exception(400, f"Please use songs that have similar BPM. Max diff is {config['max_bpm_diff']}")
    if abs(bpm_a - desired_bpm) > config['max_bpm_diff'] or abs(bpm_b - desired_bpm) > config['max_bpm_diff']:
        raise_exception(400, f"Please use a different value for your desired BPM. Max diff is {config['max_bpm_diff']}")

    mix_name = controller.generate_safe_mix_name(config, mix_name, desired_bpm, scenario_name)
    return controller.mix_two_files(config, song_a_name, song_b_name, bpm_a, bpm_b, desired_bpm, mix_name,
                                    scenario_name, transition_length, transition_midpoint)


@app.post("/adjustTempo")
async def adjust_tempo(song_name: str = Body(default=""),
                       bpm: float = Body(default=0.0)):
    if song_name == "" or bpm == 0:
        raise_exception(422, "Please provide two attributes in JSON: 'song_name' and 'bpm'")

    if not os.path.isfile(f"{config['song_path']}/{song_name}"):
        raise_exception(404, "The given song could not be found. "
                             "Please check using GET '/songs' which songs exist.")

    old_bpm = convert_bpm(util.get_bpm_from_filename(song_name))
    desired_bpm = convert_bpm(bpm)

    song_name = ''.join(song_name.split('_')[:-1])
    new_song_name = bpmMatch.adjust_tempo(config, song_name, old_bpm, desired_bpm)

    return {
        "filename": new_song_name + '.wav',
        "info": "Please refer to this name, when calling '/createMix'"
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


@app.get("/evaluation")
async def get_evaluation():
    return evaluator.get_evaluation_points()


@app.post("/evaluation")
async def set_evaluation(tsl_list: list = Body(default=[]), transition_points: dict = Body(default={})):
    if len(tsl_list) != 2 or transition_points == {}:
        raise_exception(400, "Please provide a tsl_list with two elements and the transition points a, c, d & e.")

    return evaluator.set_evaluation_points(tsl_list, transition_points)
