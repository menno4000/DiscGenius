# for converting files you will need ffmpeg and LAME
# https://ffmpeg.org/
# http://lame.sourceforge.net/

import os


def convert_wav_to_mp3(config, input_path, output_path, bitrate):
    cmd = f"{config['ffmpeg_path']}/ffmpeg -i \"{input_path}\" -codec:a libmp3lame -b:s {bitrate}k \"{output_path}\""
    os.system(cmd)


def convert_mp3_to_wav(config, input_path, output_path):
    cmd = f"{config['ffmpeg_path']}/ffmpeg -i \"{input_path}\" \"{output_path}\""
    os.system(cmd)


def convert_result_to_mp3(config, mix_name):
    print("INFO - Converting wav to mp3...")
    if '.wav' in mix_name:
        mix_mp3 = f"{mix_name[:-4]}.mp3"
        wav_path = f"{config['mix_path']}/{mix_name}"
        mp3_path = f"{config['mix_path']}/{mix_mp3}"
        convert_wav_to_mp3(config, wav_path, mp3_path, config['mp3_bitrate'])
        print("INFO - File was converted and is located at '%s'" % mp3_path)
        return mix_mp3
    return
