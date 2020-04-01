import glob
import os
import unittest
import wave

from starlette.testclient import TestClient

from ..api import app
from ..utility import common

EXAMPLE_AUDIO = "mini-audio"
WAV_EXTENSION = 'wav'
WAV_AUDIO_PATH = f"discgenius/tests/{EXAMPLE_AUDIO}.{WAV_EXTENSION}"
BPM = 124.36


class TestAPIUpload(unittest.TestCase):

    def setUp(self):
        self.config = common.get_config("./content.ini")
        self.client = TestClient(app)
        file = wave.open(WAV_AUDIO_PATH, 'rb')
        self.example_audio_wav = file.readframes(file.getnframes())

    def tearDown(self):
        for f in glob.glob(f"{self.config['song_path']}/min*"):
            os.remove(f)

    def test_upload_no_input(self):
        response = self.client.post("/upload")
        assert 400 == response.status_code

    def test_upload_no_filename(self):
        url_params = f"extension={WAV_EXTENSION}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "filename" in response.json()['detail']

    def test_upload_no_extension(self):
        url_params = f"filename={EXAMPLE_AUDIO}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "extension" in response.json()['detail']

    def test_upload_no_audio_file(self):
        url_params = f"filename={EXAMPLE_AUDIO}&extension={WAV_EXTENSION}&bpm={BPM}"
        response = self.client.post(f"/upload?{url_params}")
        assert 400 == response.status_code
        assert "provide" in response.json()['detail']
        assert "audio" in response.json()['detail']
        assert "file" in response.json()['detail']

    def test_filename_has_no_format(self):
        url_params = f"filename={EXAMPLE_AUDIO}&extension={WAV_EXTENSION}&bpm={BPM}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        print(response.json())
        assert f"{EXAMPLE_AUDIO}_{BPM}.{WAV_EXTENSION}" == response.json()['filename']

    def test_filename_shorter_4(self):
        filename = "min"
        url_params = f"filename={filename}&extension={WAV_EXTENSION}&bpm={BPM}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert f"{filename}_{BPM}.{WAV_EXTENSION}" == response.json()['filename']

    def test_same_filename(self):
        url_params = f"filename={EXAMPLE_AUDIO}&extension={WAV_EXTENSION}&bpm={BPM}"
        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert f"{EXAMPLE_AUDIO}_{BPM}.{WAV_EXTENSION}" == response.json()['filename']

        response = self.client.post(f"/upload?{url_params}", self.example_audio_wav)
        assert 200 == response.status_code
        assert not f"{EXAMPLE_AUDIO}_{BPM}.{WAV_EXTENSION}" == response.json()['filename']
        assert f"{EXAMPLE_AUDIO}-1_{BPM}.{WAV_EXTENSION}" == response.json()['filename']

    def test_upload_mp3_creates_wav(self):
        extension = "mp3"
        url_params = f"filename={EXAMPLE_AUDIO}&extension={extension}&bpm={BPM}"
        example_audio_mp3 = open(f"discgenius/tests/{EXAMPLE_AUDIO}.{extension}", 'rb').read()
        response = self.client.post(f"/upload?{url_params}", example_audio_mp3)
        assert 200 == response.status_code
        assert f"{EXAMPLE_AUDIO}_{BPM}.{WAV_EXTENSION}" == response.json()['filename']
        assert os.path.isfile(f"{self.config['mp3_storage']}/{EXAMPLE_AUDIO}_{BPM}.mp3")
        assert os.path.isfile(f"{self.config['song_path']}/{EXAMPLE_AUDIO}_{BPM}.wav")
