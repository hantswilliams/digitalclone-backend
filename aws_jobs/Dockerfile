FROM python:3.8    

LABEL maintainer="Hants <hantsawilliams@gmail.com>"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN apt-get update
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg

COPY ./a2h /a2h

WORKDIR /a2h/


