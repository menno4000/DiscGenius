#!/bin/bash

mkdir audio
mkdir audio/songs
mkdir audio/songs/storage
mkdir audio/mixes
mkdir audio/data
mkdir audio/data/song_analysis

export PYTHONPATH=${PYTHONPATH:-.}
echo "PYTHONPATH set to ${PYTHONPATH}"

pip install -r requirements.txt
gunicorn -k uvicorn.workers.UvicornWorker --workers=2 -t 6000 discgenius.api:app --bind=127.0.0.1:9001