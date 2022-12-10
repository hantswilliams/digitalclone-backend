import sys
import os
import string
import time
import argparse
import json
import numpy as np


import torch
from TTS.tts.utils.synthesis import synthesis
# from TTS.tts.utils.text.symbols import make_symbols, phonemes, symbols
# from TTS.tts.utils.text.symbols import phonemes, symbols
try:
  from TTS.utils.audio import AudioProcessor
except:
  from TTS.utils.audio import AudioProcessor
from TTS.tts.models import setup_model
from TTS.config import load_config
from TTS.tts.models.vits import *

OUT_PATH = 'out/'

# create output path
os.makedirs(OUT_PATH, exist_ok=True)

# model vars 
MODEL_PATH = 'best_model_latest.pth.tar'
CONFIG_PATH = 'config.json'
TTS_LANGUAGES = "language_ids.json"
TTS_SPEAKERS = "speakers.json"
USE_CUDA = torch.cuda.is_available()

# load the config
C = load_config(CONFIG_PATH)

# load the audio processor
ap = AudioProcessor(**C.audio)

speaker_embedding = None

# C.model_args['d_vector_file'] = TTS_SPEAKERS
# C.model_args['use_speaker_encoder_as_loss'] = False

# model = setup_model(C)
# model.language_manager.set_language_ids_from_file(TTS_LANGUAGES)
# # print(model.language_manager.num_languages, model.embedded_language_dim)
# # print(model.emb_l)
# cp = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
# # remove speaker encoder
# model_weights = cp['model'].copy()
# for key in list(model_weights.keys()):
#   if "speaker_encoder" in key:
#     del model_weights[key]

# model.load_state_dict(model_weights)


# model.eval()

# if USE_CUDA:
#     model = model.cuda()

# # synthesize voice
# use_griffin_lim = False



# from TTS.tts.utils.speakers import SpeakerManager
# from pydub import AudioSegment
# import librosa

# CHECKPOINT_SE_PATH = 'SE_checkpoint.pth.tar'
# CONFIG_SE_PATH = 'config_se.json'

# SE_speaker_manager = SpeakerManager(encoder_model_path=CHECKPOINT_SE_PATH, encoder_config_path=CONFIG_SE_PATH, use_cuda=USE_CUDA)

# def compute_spec(ref_file):
#   y, sr = librosa.load(ref_file, sr=ap.sample_rate)
#   spec = ap.spectrogram(y)
#   spec = torch.FloatTensor(spec).unsqueeze(0)
#   return spec


dataset_path = "/testfiles/testdatasets/audiofiles"

# get list of files in audiofiles/wavs
audiofiles = os.listdir(dataset_path + "/wavs")
# loop through each file in audiofiles/wavs and convert to 22050
for file in audiofiles:
    # get file name
    filename = file.split(".")[0]
    # get file extension
    fileext = file.split(".")[1]
    # create command to convert file to 22050
    command = "ffmpeg -i " + dataset_path + "/wavs/" + file + " -ar 16000 -ac 1 " + dataset_path + "/wavs/" + filename + "_mod." + fileext + " -y"
    # command = "ffmpeg -i " + dataset_path + "/wavs/" + file + " -ar 16000 -ac 1 " + dataset_path + "/wavs/clean/" + filename + "_mod." + fileext + " -y"
    # run command
    os.system(command)
    # print
    print("converted " + file + " to 16000")

# get list of files in audiofiles/wavs
audiofiles = os.listdir(dataset_path + "/wavs/")
# keep only files with _mod in name
audiofiles = [file for file in audiofiles if "_mod" in file]
print('converted audio files: ', audiofiles)

reference_emb = SE_speaker_manager.compute_d_vector_from_clip(audiofiles)



model.length_scale = 1  # scaler for the duration predictor. The larger it is, the slower the speech.
model.inference_noise_scale = 0.3 # defines the noise variance applied to the random z vector at inference.
model.inference_noise_scale_dp = 0.3 # defines the noise variance applied to the duration predictor z vector at inference.
text = "It took me quite a long time to develop a voice and now that I have it I am not going to be silent."


model.language_manager.language_id_mapping


language_id = 0

print(" > text: {}".format(text))
wav, alignment, _, _ = synthesis(
                    model,
                    text,
                    C,
                    "cuda" in str(next(model.parameters()).device),
                    ap,
                    speaker_id=None,
                    d_vector=reference_emb,
                    style_wav=None,
                    language_id=language_id,
                    enable_eos_bos_chars=C.enable_eos_bos_chars,
                    use_griffin_lim=True,
                    do_trim_silence=False,
                ).values()
print("Generated Audio")

file_name = text.replace(" ", "_")
file_name = file_name.translate(str.maketrans('', '', string.punctuation.replace('_', ''))) + '.wav'
out_path = os.path.join(OUT_PATH, file_name)

print(" > Saving output to {}".format(out_path))
ap.save_wav(wav, out_path)