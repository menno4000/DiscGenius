#!/bin/bash

pip install -r ../requirements.txt
uvicorn discgenius.api:app --reload --port 9001
