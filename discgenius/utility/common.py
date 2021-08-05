#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# this file is for reading the 'content.ini' which holds configuration details for the application.
# it will load these configuration details into a variable which can then be accessed.

import configparser
import sys
import logging

from . import utility as util

logger = logging.getLogger("utility.common")


def get_parser(content_path):
    parser_file_list = [content_path]
    parser = configparser.ConfigParser()
    file_list = parser.read(parser_file_list)
    if len(file_list) == 0:
        logger.info("CMERR0 missing configuration files: {}".format(parser_file_list))
        sys.exit(2)

    return parser


def get_boolean_parameter(parser, section, parameter):
    try:
        return parser.getboolean(section, parameter)
    except configparser.NoOptionError as error:
        logger.info("CMERR1 - Can't read configuration: ", error)
        raise SystemExit(1)
    except configparser.NoSectionError as error:
        logger.info("CMERR2 - Can't read configuration: ", error)
        raise SystemExit(2)


def get_string_parameter(parser, section, parameter):
    try:
        return parser.get(section, parameter)
    except configparser.NoOptionError as error:
        logger.info("CMERR3 - Can't read configuration: ", error)
        raise SystemExit(1)
    except configparser.NoSectionError as error:
        logger.info("CMERR4 - Can't read configuration: ", error)
        raise SystemExit(2)


def get_int_parameter(parser, section, parameter):
    string_parameter = get_string_parameter(parser, section, parameter)
    return int(string_parameter)


def get_float_parameter(parser, section, parameter):
    string_parameter = get_string_parameter(parser, section, parameter)
    return float(string_parameter)

def convert_to_list(s):
    return list(filter(None, map(str.strip, s.split(","))))


def get_list_parameter(parser, section, parameter):
    try:
        s = parser.get(section, parameter)
        return convert_to_list(s)
    except configparser.NoOptionError as error:
        logger.info("CMERR5 - Can't read configuration: ", error)
        raise SystemExit(1)
    except configparser.NoSectionError as error:
        logger.info("CMERR6 - Can't read configuration: ", error)
        raise SystemExit(2)


def get_config(content_path):
    parser = get_parser(content_path)
    section = "DEFAULT"
    config = {
        'sample_rate': get_int_parameter(parser, section, 'sample_rate'),
        'mp3_bitrate': get_int_parameter(parser, section, 'mp3_bitrate'),
        'stereo': get_boolean_parameter(parser, section, 'stereo'),
        'mix_area': get_float_parameter(parser, section, 'mix_area'),
        'clip_size': get_int_parameter(parser, section, 'clip_size'),
        'step_size': get_int_parameter(parser, section, 'step_size'),
        'min_segment_time': get_int_parameter(parser, section, 'min_segment_time'),
        'secret': get_string_parameter(parser, section, 'secret'),
        'db_name': get_string_parameter(parser, section, 'db_name'),
        'user_col': get_string_parameter(parser, section, 'user_col'),
        'tracks_col': get_string_parameter(parser, section, 'tracks_col'),
        'mixes_col': get_string_parameter(parser, section, 'mixes_col'),
        'mongo_url': get_string_parameter(parser, section, 'mongo_url'),
        'data_path': get_string_parameter(parser, "PATHS", 'data_path'),
        'song_path': get_string_parameter(parser, "PATHS", 'song_path'),
        'song_analysis_path': get_string_parameter(parser, "PATHS", 'song_analysis_path'),
        'mp3_storage': get_string_parameter(parser, "PATHS", 'mp3_storage'),
        'mix_path': get_string_parameter(parser, "PATHS", 'mix_path'),
        'scenario_path': get_string_parameter(parser, "PATHS", 'scenario_path'),
        'ffmpeg_path': get_string_parameter(parser, "PATHS", 'ffmpeg_path'),
        'info_text_path': get_string_parameter(parser, "PATHS", 'info_text_path'),

        'audio_formats': get_list_parameter(parser, "LISTS", 'audio_formats'),
        'keys_to_remove': get_list_parameter(parser, "LISTS", 'keys_to_remove'),

        'max_bpm': get_float_parameter(parser, "BPM_LIMITS", 'max_bpm'),
        'min_bpm': get_float_parameter(parser, "BPM_LIMITS", 'min_bpm'),
        'max_bpm_diff': get_float_parameter(parser, "BPM_LIMITS", 'max_bpm_diff')
    }
    config['scenarios'] = util.get_scenarios(config, True)
    return config
