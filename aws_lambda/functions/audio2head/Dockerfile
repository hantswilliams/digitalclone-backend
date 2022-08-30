FROM public.ecr.aws/lambda/python:3.8   
LABEL maintainer="Hants <hantsawilliams@gmail.com>"
RUN yum -y update && yum -y install libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg gcc gcc-c++ mesa-libGL 

# Install ffmpeg
# RUN curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz -s
# Note that we use a local copy of ffmpeg in this example to avoid downloading it, which sometimes errors out.
RUN yum -y install tar xz unzip
COPY ffmpeg.tar.xz .
RUN tar -xf ffmpeg.tar.xz
RUN mv ffmpeg-*-amd64-static/ffmpeg /usr/bin

COPY requirements_a2h.txt .
RUN pip install -r requirements_a2h.txt --target "${LAMBDA_TASK_ROOT}"

# copy application code 
COPY ./a2h ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}

# # navigate to checkpoints directory and run: wget --no-check-certificate --no-proxy https://nhit-public.s3.us-east-2.amazonaws.com/audio2head.pth.tar
# # first see if build file is < 10gb, if it is, can keep it in a2h folder and not download it 
# WORKDIR /a2h/checkpoints
# RUN wget --no-check-certificate --no-proxy https://nhit-public.s3.us-east-2.amazonaws.com/audio2head.pth.tar

CMD ["app.lambda_handler"]

