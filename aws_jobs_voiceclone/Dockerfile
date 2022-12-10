# FROM python:3.9    

# LABEL maintainer="Hants <hantsawilliams@gmail.com>"

# COPY requirements.txt /requirements.txt
# RUN pip install -r /requirements.txt

# RUN apt-get update
# RUN apt-get install libsndfile-dev -y

# COPY ./tts /tts-custom

# WORKDIR /tts-custom

# RUN pip install protobuf==3.20.0



# below is official dockerfile from https://github.com/coqui-ai/TTS/blob/dev/Dockerfile 

ARG BASE=nvcr.io/nvidia/pytorch:22.03-py3
FROM ${BASE}
LABEL maintainer="Hants <hantsawilliams@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make  python3 python3-dev python3-pip python3-venv python3-wheel espeak espeak-ng libsndfile1-dev && rm -rf /var/lib/apt/lists/*
RUN pip install llvmlite --ignore-installed

# Create and activate virtual env
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -U pip setuptools wheel

WORKDIR /root
COPY requirements.txt /root
COPY requirements.dev.txt /root
COPY requirements.notebooks.txt /root
RUN ["/bin/bash", "-c", "pip install -r <(cat requirements.txt requirements.dev.txt requirements.notebooks.txt)"]
COPY . /root
RUN make install
ENTRYPOINT ["tts"]
CMD ["--help"]
