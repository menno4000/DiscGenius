#!/bin/bash

pip install -r ../requirements.txt
uvicorn api:app --reload --port 9001
