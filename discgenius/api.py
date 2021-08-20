import os
from http import HTTPStatus
import asyncio
import logging

import jwt
import uvicorn
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks, WebSocket, WebSocketDisconnect, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase
from motor.motor_asyncio import AsyncIOMotorGridFSBucket, AsyncIOMotorClient
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import FileResponse, StreamingResponse

from . import controller
from .utility import bpm_detection
from .utility import common, bpm_match, validator
from .utility import utility as util
from .utility.audio_file_converter import convert_audio_to_wav, convert_wav_to_mp3
from .utility.db import db
from .utility.fastapi.user_model import UserDB, UserCreate, UserUpdate, User
from .utility.model import song_helper, mix_helper, response_model, error_response_model
from .utility.mongodb import ConnectionManager
from pathlib import Path


logger = logging.getLogger()
logger.name = "discgenius"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s [%(levelname).1s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

config = common.get_config('./content.ini')
SCENARIOS = util.get_scenarios(config, just_names=True)
USERNAME = os.getenv("DG_DB_USERNAME")
PASSWORD = os.getenv("DG_DB_PASSWORD")
address = os.getenv("DG_DB_ADDRESS")
logger.info(f"mongodb username: {USERNAME}")

if not address:
    address = config['mongo_url']
DATABASE_URL = f"mongodb://{address}"

SECRET = config['secret']
DATABASE_NAME = config['db_name']
USER_DB = config['user_col']
SONGS_DB = config['tracks_col']
MIX_DB = config['mixes_col']
PREVIEWS = config['previews']
manager = ConnectionManager()
CHUNK_SIZE = 1024*1024


def on_after_register(user: UserDB, request: Request):
    logger.info(f"User {user.id} has registered.")
    logger.info(f"user track")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    logger.info(f"User {user.id} has forgot their password. Reset token: {token}")


def after_verification_request(user: UserDB, token: str, request: Request):
    logger.info(f"Verification requested for user {user.id}. Verification token: {token}")


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=86400, tokenUrl="auth/jwt/login"
)

# jobs: Dict[UUID, Job] = {}
app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://menno4000.github.io/discgenius-app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/resources", StaticFiles(directory="resources"), name="resources")

user_db: MongoDBUserDatabase = None
track_client: AsyncIOMotorClient = None
song_db: Collection = None
mix_db: Collection = None
fastapi_users = None
fs: AsyncIOMotorGridFSBucket = None


async def chunk_generator(grid_out):
    while True:
        # chunk = await grid_out.read(1024)
        chunk = await grid_out.readchunk()
        if not chunk:
            break
        yield chunk


async def download_file_stream(file_id):
    """Returns iterator over AsyncIOMotorGridOut object"""
    global fs
    grid_out = await fs.open_download_stream(file_id)
    return chunk_generator(grid_out)


async def download_file(file_id):
    cursor = fs.find({"filename": file_id})
    song_data = b""
    async for grid_data in cursor:
        song_data = grid_data.read()
    with open(file_id, 'wb') as f:
        f.write(song_data)
    return file_id


async def clean_up_file(file_id):
    await asyncio.sleep(300)
    os.remove(file_id)


@app.on_event("startup")
async def startup():
    await db.connect_to_database(path=DATABASE_URL, username=USERNAME, password=PASSWORD)
    global track_client
    track_client = db.client
    disc_db = db.client[DATABASE_NAME]
    global fs
    fs = AsyncIOMotorGridFSBucket(disc_db)

    global song_db
    song_db = disc_db.get_collection(SONGS_DB)

    global mix_db
    mix_db = disc_db.get_collection(MIX_DB)

    user_col = disc_db[USER_DB]
    global user_db
    user_db = MongoDBUserDatabase(UserDB, user_col)
    global fastapi_users
    fastapi_users = FastAPIUsers(
        user_db,
        [jwt_authentication],
        User,
        UserCreate,
        UserUpdate,
        UserDB
    )

    app.include_router(
        fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_register_router(
            after_register=on_after_register
        ),
        prefix="/auth",
        tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_reset_password_router(
            SECRET, after_forgot_password=on_after_forgot_password
        ),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(
            SECRET, after_verification_request=after_verification_request
        ),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(),
        prefix="/users",
        tags=["users"])

    # check for previews in db
    preview_names = [(preview + '.mp3') for preview in PREVIEWS]
    for scenario, prev_name in zip(PREVIEWS, preview_names):
        prev_db_obj = fs.find({"filename": str(prev_name)})
        song_data = b""
        async for grid_data in prev_db_obj:
            song_data = grid_data.read()
        if not song_data:
            # write non existent previews to db
            logger.info(f"preview for scenario {scenario} not found, writing to db.")
            prev_path = './resources/preview_' + prev_name
            with open(prev_path, 'rb') as f:
                grid_in = fs.open_upload_stream(prev_name)
                await grid_in.write(f.read())
                await grid_in.close()
            logger.debug(f"preview file {prev_name} written to db grid fs.")


@app.on_event("shutdown")
async def shutdown():
    await db.close_database_connection()
    app.state.executor.shutdown()


def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


def save_song(config, filename, song_data):
    with open(f"{config['song_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


def save_temp_song(config, filename, song_data):
    with open(f"{config['song_analysis_path']}/{filename}", mode='bx') as f:
        f.write(song_data)


@app.post("/upload")
async def upload_song(request: Request,
                      filename: str = "",
                      extension: str = "",
                      bpm: str = "",
                      # file: bytes = Form(...)
                      ):
    body = await request.body()

    if filename == "" or extension == "":
        raise_exception(400, "Please provide a filename and the extension (format) of the song as query parameters.")
    if not body:
        raise_exception(400, "Please provide an audio file as a binary file.")
    if extension not in config['audio_formats']:
        raise_exception(400, "Audio format not supported. Please provide one of the following formats: %s" % config[
            'audio_formats'])

    # get auth data
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"receiving upload from user {user_id}")
    # TODO get similar song names from grid fs for safe song creation

    # create temp file to run bpm detection on
    _temp_filename = controller.generate_safe_song_temp_name(config, filename, extension)
    temp_mp3_path = ""
    save_temp_song(config, _temp_filename, body)

    if extension == 'mp3':
        temp_filename = controller.generate_safe_song_temp_name(config, filename, 'wav')
        temp_mp3_path = f"{config['song_analysis_path']}/{_temp_filename}"
        temp_wav_path = f"{config['song_analysis_path']}/{temp_filename}"
        convert_audio_to_wav(config, temp_mp3_path, temp_wav_path)
    else:
        # TODO create mp3 song file for playback
        temp_filename = _temp_filename
        _temp_filename = f'{str(_temp_filename)[:-4]}.mp3'
        temp_mp3_path = f"{config['song_analysis_path']}/{_temp_filename}"
        temp_wav_path = f"{config['song_analysis_path']}/{temp_filename}"
        convert_wav_to_mp3(config, temp_wav_path, temp_mp3_path)

    if bpm == "":
        bpm = bpm_detection.estimate_tempo(config, temp_filename, 3)

    bpm = validator.convert_bpm(config, bpm)
    song_length = util.get_song_length(config, temp_filename)

    _filename = await controller.generate_safe_song_name(config, filename, 'wav', bpm, song_db)

    logger.info(f"saving track {_filename} to gridfs")
    with open(temp_wav_path, 'rb') as f:
        grid_in = fs.open_upload_stream(
            _filename)
        await grid_in.write(f.read())
        await grid_in.close()

    if temp_mp3_path:
        with open(temp_mp3_path, 'rb') as f:
            grid_in = fs.open_upload_stream(
                _temp_filename)
            await grid_in.write(f.read())
            await grid_in.close()

    logger.info(f"saving song object to song db")
    song_data = {
        "title": str(_filename),
        "length": str(song_length),
        "bpm": float(bpm),
        "user_id": str(user_id),
    }
    if temp_mp3_path:
        song_data['title_mp3'] = _temp_filename
    song_id = await song_db.insert_one(song_data)

    # remove bpm detection temp files
    if temp_mp3_path:
        os.remove(temp_mp3_path)
    #     # shutil.move(temp_wav_path, f"{config['song_path']}/{_filename}")
    # else:
    #     # save_song(config, _filename, body)
    os.remove(temp_wav_path)
    response = {
        "filename": _filename,
        "bpm": str(bpm),
        "length": str(song_length),
        "id": str(song_id.inserted_id)
    }

    return response


# @app.post("/extendMix")
# async def extendMix(mix_a_name: str = Body(default=""), song_b_name: str = Body(default=""),
#                     mix_name: str = Body(default=""),
#                     scenario_name: str = Body(default="EQ_1.0"),
#                     bpm: float = Body(default=0),
#                     transition_length: int = Body(default=32),
#                     transition_midpoint: int = Body(default=16),
#                     transition_points: dict = Body(default=None),
#                     entry_point: float = Body(default=config['mix_area'])):
#     if mix_a_name == "" or song_b_name == "" or scenario_name == "":
#         raise_exception(status_code=422, detail=util.read_api_detail(config))
#
#     if not os.path.isfile(f"{config['mix_path']}/{mix_a_name}") or not os.path.isfile(
#             f"{config['song_path']}/{song_b_name}"):
#         raise_exception(404, "One of the two given songs could not be found. "
#                              "Please check using GET '/songs' which songs exist.")
#
#     # TODO retrieve number of included songs from song description json
#     num_songs_a, bpm_a = util.read_mix_content_data(config, mix_a_name)
#     if bpm == 0:
#         desired_bpm = bpm_a
#     else:
#         desired_bpm = bpm
#
#     if scenario_name not in SCENARIOS:
#         raise_exception(422, "Transition scenario could not be found.")
#
#     exit_point_modifier = entry_point / num_songs_a
#     exit_point = 1 - exit_point_modifier
#
#     if exit_point < 0.0 or exit_point > 1.0 or entry_point < 0.0 or entry_point > 1.0:
#         raise_exception(422, "exit_point or entry_point must be floating point numbers between 0 and 1.")
#
#     bpm_a, bpm_b, desired_bpm = validator.validate_bpms_extend(config, song_b_name, bpm_a, desired_bpm)
#
#     transition_length, transition_midpoint, transition_points = validator.validate_transition_times(config,
#                                                 mix_a_name,
#                                                                                                     song_b_name)
#     config['transition_length'] = transition_length
#     config['transition_midpoint'] = transition_midpoint
#
#     mix_name = controller.generate_safe_mix_name(config, mix_name, desired_bpm, scenario_name)
#
#     logger.info(f"INFO - A new mix will get created from songs '{mix_a_name}' & '{song_b_name}'.")
#     logger.info(
#         f"       Transition length: {transition_length}, Transition midpoint: {transition_midpoint}, Desired bpm: '{desired_bpm}'.")
#     logger.info(f"       Mix name: '{mix_name}'.")
#     logger.info()
#
#     return controller.mix_two_files(config, mix_a_name, song_b_name, bpm_a, bpm_b, desired_bpm, mix_name, scenario_name,
#                                     transition_points, entry_point, exit_point, num_songs_a)

# TODO true async


@app.post("/createMix", status_code=HTTPStatus.ACCEPTED)
async def mix(request: Request,
              background_tasks: BackgroundTasks,
              song_a_name: str = "",
              song_b_name: str = "",
              mix_name: str = "",
              scenario_name: str = "EQ_1.0",
              bpm: float = 0,
              transition_length: int = 32,
              transition_midpoint: int = 16,
              transition_points: dict = None,
              num_songs_a: int = 1,
              num_songs_b: int = 1,
              exit_point: float = config['mix_area'],
              entry_point: float = config['mix_area'],
              ):
    # get auth data
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"receiving create mix request from user {user_id}")

    if song_a_name == "" or song_b_name == "" or scenario_name == "":
        raise_exception(status_code=422, detail=util.read_api_detail(config))

    if num_songs_a > 1:
        exit_point = exit_point / num_songs_a
        _song_a = await mix_db.find_one({"title": str(song_a_name)})
    else:
        _song_a = await song_db.find_one({"title": str(song_a_name)})
    if not _song_a:
        raise_exception(404,
                        "track A could not be found. Please check using GET '/mixes' or GET '/songs' which tracks "
                        "exist.")

    if num_songs_b > 1:
        entry_point = entry_point / num_songs_b
        _song_b = await mix_db.find_one({"title": str(song_b_name)})
    else:
        _song_b = await song_db.find_one({"title": str(song_b_name)})
    if not _song_b:
        raise_exception(404,
                        "track B could not be found. Please check using GET '/mixes' or GET '/songs' which tracks "
                        "exist.")

    if scenario_name not in SCENARIOS:
        raise_exception(422, "Transition scenario could not be found.")

    exit_point = 1 - exit_point

    if exit_point < 0.0 or exit_point > 1.0 or entry_point < 0.0 or entry_point > 1.0:
        raise_exception(422, "exit_point or entry_point must be floating point numbers between 0 and 1.")

    bpm_a, bpm_b, desired_bpm = validator.validate_bpms_create(config,
                                                               song_a_name,
                                                               num_songs_a,
                                                               song_b_name,
                                                               num_songs_b,
                                                               bpm)

    transition_length, transition_midpoint, transition_points = validator.validate_transition_times(config,
                                                                                                    transition_length,
                                                                                                    transition_midpoint,
                                                                                                    transition_points,
                                                                                                    desired_bpm,
                                                                                                    song_a_name,
                                                                                                    song_b_name)
    # TODO investigate workaround for permanent config change
    config['transition_length'] = transition_length
    config['transition_midpoint'] = transition_midpoint

    mix_name = controller.generate_safe_mix_name(config, mix_name, desired_bpm, scenario_name, transition_length,
                                                 transition_midpoint)

    song_list = []
    scenario_list = []
    if num_songs_a > 1:
        song_list.extend(_song_a['song_list'])
        scenario_list.extend(_song_a['scenario_list'])
        transition_points_a = _song_a['transition_points']
    else:
        song_list.append(song_a_name.split('_')[0])
        transition_points_a = []
    scenario_list.append(scenario_name)
    if num_songs_b > 1:
        song_list.extend(_song_b['song_list'])
        scenario_list.extend(_song_b['scenario_list'])
        transition_points_b = _song_b['transition_points']
    else:
        song_list.append(song_b_name.split('_')[0])
        transition_points_b = []


    logger.debug("saving initial mix object to mix db")
    mix_id = await mix_db.insert_one({
        "title": str(mix_name),
        "bpm": float(desired_bpm),
        "num_songs": int((num_songs_a + num_songs_b)),
        "transition_length": int(transition_length),
        "transition_midpoint": int(transition_midpoint),
        "user_id": str(user_id),
        "song_list": song_list,
        "scenario_list": scenario_list,
        "progress": int(10)
    })

    logger.info(f"INFO - A new mix will get created from songs '{song_a_name}' & '{song_b_name}'.")
    logger.info(
        f"       Transition length: {transition_length}, Transition midpoint: {transition_midpoint}, Desired bpm: '{desired_bpm}'.")
    logger.info(f"       Mix name: '{mix_name}'.")
    logger.info("")

    # new_task = Job()
    # jobs[new_task.uid] = new_task
    param = {
        'config': config,
        'song_a_name': song_a_name,
        'song_b_name': song_b_name,
        'bpm_a': bpm_a,
        'bpm_b': bpm_b,
        'desired_bpm': desired_bpm,
        'mix_name': mix_name,
        'scenario_name': scenario_name,
        'transition_points': transition_points,
        'exit_point': exit_point,
        'entry_point': entry_point,
        'num_songs_a': num_songs_a,
        'num_songs_b': num_songs_b,
        'mix_id': mix_id.inserted_id,
        'mix_db': mix_db,
        'fs': fs,
        'tps_a': transition_points_a,
        'tps_b': transition_points_b,
    }

    background_tasks.add_task(controller.mix_two_files, param)
    return {"message": f"Mix creation for {mix_name} started: ID: {mix_id.inserted_id} "}
    # return new_task

    # return await controller.mix_two_files(config,
    #                                       song_a_name,
    #                                       song_b_name,
    #                                       bpm_a,
    #                                       bpm_b,
    #                                       desired_bpm,
    #                                       mix_name,
    #                                       scenario_name,
    #                                       transition_points,
    #                                       entry_point,
    #                                       exit_point,
    #                                       num_songs_a,
    #                                       mix_id.inserted_id,
    #                                       mix_db,
    #                                       fs)


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
    new_song_name = bpm_match.adjust_tempo(config, song_name, old_bpm, desired_bpm)

    return {
        "filename": new_song_name,
        "info": f"A copy of the original song was created in a new tempo ({desired_bpm}). Please refer to this name, when calling '/createMix'"
    }


@app.get("/getMixObject/{mix_id}")
async def get_mix_object(mix_id: str = ""):
    if mix_id == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    mix_object = ""
    cursor = mix_db.find({"_id": ObjectId(mix_id)})
    async for m in cursor:
        mix_object = mix_helper(m)

    if mix_object:
        return response_model(mix_object, f"retrieved mix of id {mix_id}.")


@app.get("/getMix")
async def get_mix(background_tasks: BackgroundTasks, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    file = await download_file(name)
    if file:
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        response = FileResponse(file, media_type=content_type)
        background_tasks.add_task(clean_up_file, file)
        return response
    else:
        return error_response_model("Not Found", "404", "Mix not found")


@app.get("/getMixBytes/{name}")
async def get_mix_bytes(background_tasks: BackgroundTasks, request: Request, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the preview name url parameter .")
    file = await download_file(name)
    if file:
        byte_range = request.headers['Range']
        start, end = byte_range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else start + CHUNK_SIZE
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        audio_path = Path(name)
        with open(audio_path, "rb") as audio:
            audio.seek(start)
            data = audio.read(end - start)
            filesize = str(audio_path.stat().st_size)
            headers = {
                'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                'Accept-Ranges': 'bytes'
            }
            response = Response(data, status_code=206, media_type=content_type, headers=headers)
            background_tasks.add_task(clean_up_file, file)
            # os.remove(file)
            return response
    else:
        return error_response_model("Not Found", "404", "Mix not found")


@app.get("/mixPreview/{preview_name}")
async def get_preview_media(request: Request, background_tasks: BackgroundTasks, preview_name: str = ''):

    if preview_name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    file = await download_file(preview_name)
    if file:
        byte_range = request.headers['Range']
        start, end = byte_range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else start + CHUNK_SIZE
        audio_path = Path(preview_name)
        with open(audio_path, "rb") as audio:
            audio.seek(start)
            data = audio.read(end - start)
            filesize = str(audio_path.stat().st_size)
            headers = {
                'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                'Accept-Ranges': 'bytes'
            }
            response = Response(data, status_code=206, media_type='audio/mpeg', headers=headers)
            background_tasks.add_task(clean_up_file, file)
            # os.remove(file)
            return response
    else:
        raise HTTPException(status_code=400, detail="Scenario name not recognized.")


@app.get("/getMixMedia/{name}")
async def get_mix_media(background_tasks: BackgroundTasks, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    file = await download_file(name)
    if file:
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        grid_out = await fs.open_download_stream_by_name(name)
        response = StreamingResponse(chunk_generator(grid_out), media_type=content_type, headers={
            'Accept-Ranges': 'bytes'
        })
        background_tasks.add_task(clean_up_file, file)
        return response
    else:
        return error_response_model("Not Found", "404", "Mix not found")


@app.get("/getSong/{name}")
async def get_song(background_tasks: BackgroundTasks, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    file = await download_file(name)
    if file:
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        response = FileResponse(file, media_type=content_type)
        background_tasks.add_task(clean_up_file, file)
        return response
    else:
        return error_response_model("Not Found", "404", "Song not found")


@app.get("/getSongBytes/{name}")
async def get_song_bytes(background_tasks: BackgroundTasks, request: Request, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")
    file = await download_file(name)
    if file:
        byte_range = request.headers['Range']
        start, end = byte_range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else start + CHUNK_SIZE
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        audio_path = Path(name)
        with open(audio_path, "rb") as audio:
            audio.seek(start)
            data = audio.read(end - start)
            filesize = str(audio_path.stat().st_size)
            headers = {
                'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                'Accept-Ranges': 'bytes'
            }
            response = Response(data, status_code=206, media_type=content_type, headers=headers)
            background_tasks.add_task(clean_up_file, file)
            # os.remove(file)
            return response
    else:
        return error_response_model("Not Found", "404", "Song not found")


@app.get("/getSongMedia/{name}")
async def get_song(background_tasks: BackgroundTasks, name: str = ""):
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name'.")
    file = await download_file(name)
    if file:
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")
        grid_out = await fs.open_download_stream_by_name(name)
        response = StreamingResponse(chunk_generator(grid_out), media_type=content_type, headers={
            'Accept-Ranges': 'bytes'
        })
        background_tasks.add_task(clean_up_file, file)
        return response
    else:
        return error_response_model("Not Found", "404", "Song not found")


@app.websocket("/getSong/ws")
async def websocket_endpoint(background_tasks: BackgroundTasks, websocket: WebSocket, request: Request, name: str = ""):
    # get auth data
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"receiving playback request from user {user_id}")
    if name == "":
        raise HTTPException(status_code=400, detail="Please provide the query param: 'name_of_mix'.")

    file = await song_db.find({'title_mp3': name})
    if file:
        file_suffix = name.split('.')[-1]
        if file_suffix == 'mp3':
            content_type = 'audio/mpeg'
        elif file_suffix == 'wav':
            content_type = 'audio/wav'
        else:
            raise HTTPException(status_code=422, detail="File ending not supported.")

        grid_out = await fs.open_download_stream_by_name(name)
        chunks = chunk_generator(grid_out).read()

        await manager.connect(websocket)
        try:
            while True:
                incoming_data = await websocket.receive_text()
                await manager.send_personal_message(f"Download Request received", websocket)
                await manager.broadcast('b')
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Playback connection stopped for user {id}: {name}")
            background_tasks.add_task(clean_up_file, file)
    else:
        return error_response_model("Not Found", "404", "Song not found")


@app.get("/songs")
async def get_songs(request: Request):
    # get auth data
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"providing song list request from user {user_id}")
    songs = []
    cursor = song_db.find({"user_id": f"{user_id}"})
    async for song in cursor:
        songs.append(song_helper(song))

    if songs:
        return response_model(songs, f"retrieved {len(songs)} songs.")
    else:
        return response_model(songs, "no songs present.")
    # return [f for f in os.listdir(config['song_path']) if isfile(join(config['song_path'], f)) and '.wav' in f]


@app.delete("/songs")
async def delete_song(request: Request, target_id: str = ""):
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"providing song list request for user {user_id}")
    songs = []
    cursor = song_db.find({
        "user_id": f"{user_id}"})
    async for song in cursor:
        if song['_id'] == ObjectId(target_id):
            songs.append(song_helper(song))
    if songs:
        if len(songs) < 2:
            song_filename = songs[0]['title']
            song_file_id = await fs.upload_from_stream(song_filename, b"")
            await fs.delete(song_file_id)
            await song_db.delete_one({
                "_id": ObjectId(target_id)})

            song_path = f"{config['song_path']}/{song_filename}"
            if os.path.isfile(song_path):
                os.remove(song_path)

            return response_model(songs[0], f"Song with id {target_id} deleted")
        else:
            return error_response_model("Internal Server Error", 500, f"Multiple options for song id{target_id}")
    else:
        return error_response_model("Not Found", 404, f"Song with id {target_id} does not exist")


@app.get("/mixes")
async def get_mixes(request: Request):
    # get auth data
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"providing song list request from user {user_id}")
    mixes = []
    cursor = mix_db.find({"user_id": f"{user_id}"})
    async for mix in cursor:
        mixes.append(mix_helper(mix))

    if mixes:
        return response_model(mixes, f"retrieved {len(mixes)} mixes.")
    else:
        return response_model(mixes, "no mixes present.")
    # return [f for f in os.listdir(config['mix_path']) if isfile(join(config['mix_path'], f)) and '.mp3' in f]


# noinspection PyUnresolvedReferences
@app.delete("/mixes")
async def delete_mixes(request: Request, target_id: str = ""):
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[-1]
    auth_token_data = jwt.decode(auth_token, SECRET, algorithms=['HS256'], audience="fastapi-users:auth")
    user_id = auth_token_data['user_id']
    logger.info(f"providing song list request for user {user_id}")
    mixes = []
    cursor = mix_db.find({
        "user_id": f"{user_id}"})
    async for mix in cursor:
        if mix['_id'] == ObjectId(target_id):
            mixes.append(song_helper(mix))
    if mixes:
        if len(mixes) < 2:
            mix_filename = mixes[0]['title']
            mix_file_id = await fs.upload_from_stream(mix_filename, b"")
            await fs.delete(mix_file_id)

            mix_path = f"{config['mix_path']}/{mix_filename}"
            if os.path.isfile(mix_path):
                os.remove(mix_path)

            if 'title_mp3' in mixes[0]:
                mix_filename_mp3 = mixes[0]['title_mp3']
                mix_file_id_mp3 = await fs.upload_from_stream(mix_filename, b"")
                await fs.delete(mix_file_id_mp3)
                await mix_db.delete_one({
                    "_id": ObjectId(target_id)})
                mix_path_mp3 = f"{config['mix_path']}/{mix_filename_mp3}"
                if os.path.isfile(mix_path_mp3):
                    os.remove(mix_path_mp3)

            await mix_db.delete_one({
                "_id": ObjectId(target_id)})

            return response_model(mixes[0], f"Mix with id {target_id} deleted")
        else:
            return error_response_model("Internal Server Error", 500, f"Multiple options for mix id{target_id}")
    else:
        return error_response_model("Not Found", 404, f"Mix with id {target_id} does not exist")


@app.get("/scenarios")
async def get_scenarios():
    return util.get_scenarios(config, just_names=False)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9001, log_level='debug')
