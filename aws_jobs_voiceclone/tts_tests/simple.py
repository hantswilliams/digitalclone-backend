import os

from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.config.shared_configs import BaseAudioConfig
from TTS.utils.audio import AudioProcessor
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.tts.models.vits import Vits
from TTS.tts.configs.vits_config import VitsConfig
from trainer import Trainer, TrainerArgs
from TTS.tts.datasets import load_tts_samples


########################################
########################################
########################################
######## Local testing file ############
########################################
########################################
########################################


###### defaults ######
# dataset_path = "/Users/hantswilliams/Documents/digitalclone-backend/aws_jobs_voiceclone/tts/testdatasets/audiofiles/"
# output_path = "/Users/hantswilliams/Documents/digitalclone-backend/aws_jobs_voiceclone/tts/testdatasets/trainoutput/"
dataset_path = "/testfiles/testdatasets/audiofiles"
output_path = "/testfiles/testdatasets/trainoutput"

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
    # run command
    os.system(command)
    # print
    print("converted " + file + " to 16000")





tpower = 1.3
tpreemphasis = 0.98
tdb = 20
######################


dataset_config = BaseDatasetConfig(
    name="ljspeech", meta_file_train='metaData_list1_1664477626975..txt', path=os.path.join(output_path, dataset_path)
)

audio_config = BaseAudioConfig(
    sample_rate=22050, 
    win_length=1024, 
    hop_length=256, 
    num_mels=80, 
    mel_fmin=0, 
    mel_fmax=None, 
    power=tpower,
    preemphasis=tpreemphasis,
    ref_level_db=tdb
)

config = VitsConfig(
    audio=audio_config,
    run_name="vits_ljspeech",
    batch_size=32,
    eval_batch_size=16,
    batch_group_size=5,
    num_loader_workers=8,
    num_eval_loader_workers=4,
    run_eval=True,
    test_delay_epochs=-1,
    epochs=1000,
    text_cleaner="english_cleaners",
    use_phonemes=True,
    phoneme_language="en-us",
    phoneme_cache_path=os.path.join(output_path, "phoneme_cache"),
    compute_input_seq_cache=True,
    print_step=25,
    print_eval=True,
    mixed_precision=True,
    output_path=output_path,
    datasets=[dataset_config],
    cudnn_benchmark=False
)



train_samples, eval_samples = load_tts_samples(
    dataset_config,
    eval_split=True,
    eval_split_max_size=config.eval_split_max_size,
    # eval_split_size=config.eval_split_size
    eval_split_size=0.1
)

ap = AudioProcessor.init_from_config(config)
tokenizer, config = TTSTokenizer.init_from_config(config)
model = Vits(config, ap, tokenizer, speaker_manager=None)


trainer = Trainer(
    TrainerArgs(), config, output_path, model=model, train_samples=train_samples, eval_samples=eval_samples
)

trainer.fit()