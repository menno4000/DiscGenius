from pydantic import BaseModel, Field
from bson import ObjectId, Binary


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class SongSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    title_mp3: str = Field(...)
    bpm: float = Field(..., le=2.0)
    user_id: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Suki.wav",
                "title_mp3": "Suki.mp3",
                "bpm": 124.0,
                "user_id": "33c00ea1-f6c1-4842-a625-a7be4ed7cf95",
            }
        }


def song_helper(song) -> dict:
    data = {
        "id": str(song['_id']),
        "title": str(song['title']),
        "bpm": float(song['bpm']),
        "user_id": str(song['user_id'])
    }
    if 'title_mp3' in song:
        data['title_mp3'] = str(song['title_mp3'])

    return data


class MixSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    title_mp3: str = Field(...)
    bpm: float = Field(..., le=2.0)
    num_songs: int = Field(...)
    scenarios: list = Field(...)
    transition_points: dict = Field(...)
    transition_length: int = Field(...)
    transition_midpoint: int = Field(...)
    progress: int = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Suki.wav",
                "title_mp3": "Suki.mp3",
                "bpm": 124.0,
                "num_songs": 2,
                "scenarios": [],
                "transition_points": {},
                "transition_length": 32,
                "transition_midpoint": 16,
                "user_id": "33c00ea1-f6c1-4842-a625-a7be4ed7cf95",
                "progress": 0
            }
        }


def mix_helper(mix) -> dict:
    mix_data = {
        "id": str(mix['_id']),
        "title": str(mix['title']),
        "bpm": float(mix['bpm']),
        "num_songs": int(mix['num_songs']),
        "transition_length": int(mix['transition_length']),
        "transition_midpoint": int(mix['transition_midpoint']),
        "user_id": str(mix['user_id']),
        "progress": int(mix['progress'])
    }
    if 'title_mp3' in mix:
        mix_data['title_mp3'] = str(mix['title'])
    if 'scenarios' in mix:
        mix_data['scenarios'] = list(mix['scenarios'])
    if 'transition_points' in mix:
        mix_data['transition_points'] = dict(mix['transition_points'])
    return mix_data


def response_model(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def error_response_model(error, code, message):
    return {"error": error, "code": code, "message": message}
