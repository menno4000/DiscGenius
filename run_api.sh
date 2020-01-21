#!/bin/bash

mkdir audio
mkdir audio/songs
mkdir audio/mixes

export PYTHONPATH=${PYTHONPATH:-.}
echo "PYTHONPATH set to ${PYTHONPATH}"

pip install -r requirements.txt
uvicorn discgenius.api:app --reload --port 9001
