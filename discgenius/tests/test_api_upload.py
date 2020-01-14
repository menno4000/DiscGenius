import glob
import os
import unittest
import wave

from starlette.testclient import TestClient

from ..api import app
from ..utility import common

EXAMPLE_AUDIO = "mini_audio.wav"
EXAMPLE_AUDIO_PATH = f"discgenius/tests/{EXAMPLE_AUDIO}"


class TestAPIUpload(unittest.TestCase):

    def setUp(self):
        self.config = common.get_config("./content.ini")
        self.client = TestClient(app)
        file = wave.open(EXAMPLE_AUDIO_PATH, 'rb')
        self.example_audio_wav = file.readframes(file.getnframes())

    def tearDown(self):
        for f in glob.glob(f"{self.config['song_path']}/min*"):
            os.remove(f)

    def test_upload_no_input(self):
        response = self.client.post("/upload")
        assert 400 == response.status_code

    def test_upload_no_filename(self):
        url_params = "extension=wav"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "filename" in response.json()['detail']

    def test_upload_no_extension(self):
        url_params = "filename=mini_audio.wav"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "extension" in response.json()['detail']

    def test_upload_no_audio_file(self):
        url_params = "filename=mini_audio.wav&extension=wav"
        response = self.client.post(f"/upload?{url_params}")
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "audio" in response.json()['detail']
        assert "file" in response.json()['detail']

    def test_filename_has_no_format(self):
        filename = "mini_audio"
        extension = "wav"
        url_params = f"filename={filename}&extension={extension}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        print(response.json())
        assert f"{filename}.{extension}" == response.json()['filename']

    def test_filename_shorter_4(self):
        filename = "min"
        extension = "wav"
        url_params = f"filename={filename}&extension={extension}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert f"{filename}.{extension}" == response.json()['filename']

    def test_same_filename(self):
        filename = "mini"
        extension = "wav"
        url_params = f"filename={filename}&extension={extension}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert f"{filename}.{extension}" == response.json()['filename']

        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert not f"{filename}.{extension}" == response.json()['filename']
        assert f"{filename}-1.{extension}" == response.json()['filename']

    def test_upload_mp3_creates_wav(self):
        filename = "mini_audio"
        extension = "mp3"
        url_params = f"filename={filename}&extension={extension}"
        example_audio_mp3 = open(f"discgenius/tests/{filename}.{extension}", 'rb').read()
        response = self.client.post(f"/upload?{url_params}", example_audio_mp3)
        assert 200 == response.status_code
        assert f"{filename}.wav" == response.json()['filename']
        assert os.path.isfile(f"{self.config['song_path']}/{filename}.mp3")
        assert os.path.isfile(f"{self.config['song_path']}/{filename}.wav")
