# Running Local Dev 

## Dockerfile 
- IMPORTANT -> when running in docker, needed to expand out available ram/memory swap that occurs to not get random `killed` errors
- Dockerfile.dev 
- Command to build image: `docker build -f Dockerfile.CPU.dev -t tts-test .` 
- Command to get container running: `docker run --rm -it -p 5002:5002 --entrypoint /bin/bash tts-test`
- Once instide of the docker image, can get a server going with gui: 
    - `python3 TTS/server/server.py --model_name tts_models/en/vctk/vits` 
- Then go inside the container and run `CUDA_VISIBLE_DEVICES=0 python /testfiles/simple.py`

## Notes 
- right now, looks like need to run the wave files through FFMPEG to do some conversion, otherwise get a missing header error 
- so inside the metaData_list1 right now, have added in `_mod` to the file names , need to automate that part later 

# Without doctor / NOT WORKING ON MY MAC PRO CURRENTLY 
- created a virtual `env` in the folder - get this running
- find where packages are in pyenv: 
    - `python -m site` - then look for the site-packages part 
- to get rid of numpy/arrayobject.h missing: `export CFLAGS="-I /Users/hantswilliams/.pyenv/versions/3.10.0/lib/python3.10/site-packages/numpy/core/include/numpy $CFLAGS"`  
- the requirements file for this is `requirements.dev.nodocker.txt`


# Google colab 
- there is a ipynb located inside of tts_tests 
- you can upload that to goolge colab - make sure to select run with `GPU` - very fast for doing 100epochs in approx 15mins / still need to do testing 