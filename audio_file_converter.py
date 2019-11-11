# for converting files you will need ffmpeg and LAME
# https://ffmpeg.org/
# http://lame.sourceforge.net/

import os


def convert_wav_to_mp3(input_path, output_path, bitrate):
    cmd = f"./ffmpeg/ffmpeg -i \"{input_path}\" -codec:a libmp3lame -b:s {bitrate}k \"{output_path}\""
    os.system(cmd)


def convert_mp3_to_wav(input_path, output_path):
    cmd = f"./ffmpeg/ffmpeg -i \"{input_path}\" \"{output_path}\""
    os.system(cmd)