FROM python:3.8.8-slim


RUN apt-get update && apt-get install -y python3-dev gcc libc-dev

RUN apt-get install -y ffmpeg

RUN mkdir app
ADD ./discgenius ./app/discgenius
# ADD required filees
ADD ./scenarios ./app/scenarios
ADD requirements.txt ./app/requirements.txt
ADD setup.py ./app/setup.py
ADD content.ini ./app/content.ini

#ADD run_api.sh ./app/run_api.sh

#RUN chmod +x ./app/run_api.sh

RUN mkdir ./app/audio
RUN mkdir ./app/audio/songs
RUN mkdir ./app/audio/songs/storage
RUN mkdir ./app/audio/mixes
RUN mkdir ./app/audio/data
RUN mkdir ./app/audio/data/song_analysis

RUN mkdir export PYTHONPATH=${PYTHONPATH:-.}

WORKDIR /app
RUN pip install --no-cache-dir .

#RUN cd /tmp/discgenius \
#    && pip3 install --no-cache-dir .

# RUN rm -r /tmp/discgenius

EXPOSE 9001

ENTRYPOINT uvicorn discgenius.api:app --port 9001