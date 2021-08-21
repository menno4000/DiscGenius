#!/bin/bash

mkdir audio
mkdir audio/songs
mkdir audio/songs/storage
mkdir audio/mixes
mkdir audio/data
mkdir audio/data/song_analysis

apt-get update && apt-get install -y python3-dev gcc libc-dev

apt-get install -y ffmpeg