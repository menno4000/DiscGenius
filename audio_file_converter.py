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


def convert_result_to_mp3(result_path, bitrate):
    print("INFO - Converting wav to mp3...")
    mp3_path = f"{result_path[:-4]}.mp3"
    convert_wav_to_mp3(result_path, mp3_path, bitrate)
    print("INFO - File was converted and is located at '%s'" % mp3_path)
