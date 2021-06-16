from pydantic import BaseModel, Field
from bson import ObjectId, Binary
import pickle


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
    bpm: float = Field(..., le=2.0)
    song_file: Binary = Field(...)
    user_id: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Suki",
                "bpm": 124.0,
                "user_id": "33c00ea1-f6c1-4842-a625-a7be4ed7cf95",
                "song_file": Binary(pickle.dumps("x"))
            }
        }


def song_helper(song) -> dict:
    return {
        "id": str(song['_id']),
        "title": str(song['title']),
        "bpm": float(song['bpm']),
        "user_id": str(song['user_id'])
    }


class Mix(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    bpm: float = Field(..., le=2.0)
    num_songs: int = Field(...)
    scenarios: list = Field(...)
    transitions: dict = Field(...)
    clip_size: int = Field(...)
    step_size: int = Field(...)


def response_model(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def error_response_model(error, code, message):
    return {"error": error, "code": code, "message": message}
