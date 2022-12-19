# https://ngbala6.medium.com/audio-processing-and-remove-silence-using-python-a7fe1552007a 

from pydub import AudioSegment
import os 
from aws_jobs_voiceclone.qualityChecks.silenceremove import read_wave, write_wave, frame_generator, vad_collector
import webrtcvad
import shutil

### TO DO: look at NOISEREDUCE - https://github.com/timsainb/noisereduce
## specifically the non-static noise reducer 

def file_converter(sound, filename, output_path):
    print("----------Before Conversion--------")
    print("Frame Rate", sound.frame_rate)
    print("Channel", sound.channels)
    print("Sample Width",sound.sample_width)
    ### example conversion 
    sound = sound.set_frame_rate(16000) # Change Frame Rate
    sound = sound.set_channels(1) # Change Channel
    sound = sound.set_sample_width(2) # Change Sample Width
    ## get file name 
    filename = filename.split("/")[-1]
    ## add _mod to filename
    filename = filename.split(".")[0] + "_mod.wav"
    output_path = os.path.join(output_path, filename)
    sound.export(output_path, format ="wav") # Export the Audio to get the changed content
    print("----------After Conversion--------")
    print("Frame Rate", sound.frame_rate)
    print("Channel", sound.channels)
    print("Sample Width",sound.sample_width)
    return print("Conversion Done")

def silence_remover(intput_file, output_path):
    ### remove silence
    audio, sample_rate, filename = read_wave(intput_file)
    print("----------Before Conversion--------")
    print("Length of audio is: ", len(audio))
    vad = webrtcvad.Vad(3) ### this sets the aggressiveness level of the VAD
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    # Segmenting the Voice audio and save it in list as bytes
    concataudio = [segment for segment in segments]
    joinedaudio = b"".join(concataudio)
    ## modify filename to include _nosilence at the end
    filename = filename.split(".")[0] + "_nosilence.wav"
    ## save path 
    filename = os.path.join(output_path, filename)
    write_wave(filename, joinedaudio, sample_rate)
    print("----------After Conversion--------")
    print("Length of audio is: ", len(joinedaudio))

### get list of all files in aws_jobs_voiceclone/tts_tests/testdata2/raw/ that end with .wav
source = "aws_jobs_voiceclone/tts_tests/testdata2/raw/"
files = os.listdir(source)
files = [f for f in files if f.endswith(".wav")]

### loop through files and convert them to 16k, 1 channel, 16 bit
for f in files:
    loadFile = AudioSegment.from_file(os.path.join(source, f))
    file_converter(loadFile, os.path.join(source, f), "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/p1_convert")

### loop through files and remove silence
source = "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/p1_convert/"
files = os.listdir(source)
files = [f for f in files if f.endswith(".wav")]
for f in files:
    silence_remover(os.path.join(source, f), "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/p2_silence")

### get all files from p2_silence folder and make a copy of them into wavs folder
source = "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/p2_silence"
destination = "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/wavs"
files = os.listdir(source)
files = [f for f in files if f.endswith(".wav")]
for f in files:
    shutil.copy(os.path.join(source, f), destination)

### remove _mod_nosilence from filename
source = "aws_jobs_voiceclone/tts_tests/testdata2/clean_quality/wavs"
files = os.listdir(source)
files = [f for f in files if f.endswith(".wav")]
for f in files:
    os.rename(os.path.join(source, f), os.path.join(source, f.replace("_mod_nosilence", ""))) 

