import os
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.config.shared_configs import BaseAudioConfig
from TTS.utils.audio import AudioProcessor
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.tts.models.vits import Vits
from trainer import Trainer, TrainerArgs

########################################
########################################
########################################
######## Local testing file ############
########################################
########################################
########################################


###### defaults ######
dataset_path = "/Users/hantswilliams/Documents/digitalclone-backend/aws_jobs_voiceclone/tts/testdatasets/audiofiles/"
output_path = "/Users/hantswilliams/Documents/digitalclone-backend/aws_jobs_voiceclone/tts/testdatasets/trainoutput/"

tpower = 1.3
tpreemphasis = 0.98
tdb = 20
######################

## test of custom formatter 
def formatter(root_path, manifest_file, **kwargs):  # pylint: disable=unused-argument
    """Assumes each line as ```<filename>|<transcription>```
    """
    txt_file = os.path.join(root_path, manifest_file)
    items = []
    speaker_name = "user"
    with open(txt_file, "r", encoding="utf-8") as ttf:
        for line in ttf:
            cols = line.split("|")
            wav_file = os.path.join(root_path, "wavs", cols[0])
            ## remove white space from right side of string wav_file
            wav_file = wav_file.rstrip()
            text = cols[1].rstrip() # the r.strip is for removing \n at the end of the line
            # remove the first white space from text on the left
            text = text.lstrip()
            items.append({"text":text, "audio_file":wav_file, "speaker_name":speaker_name})
    return items

testFormatter = formatter(dataset_path, "metaData_list1_1664477023362.txt")

    





dataset_config = BaseDatasetConfig(
    name="ljspeech", meta_file_train="metadata.csv", path=os.path.join(output_path, dataset_path)
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

ap = AudioProcessor.init_from_config(config)
tokenizer, config = TTSTokenizer.init_from_config(config)
model = Vits(config, ap, tokenizer, speaker_manager=None)
trainer = Trainer(
    TrainerArgs(), config, output_path, model=model, train_samples=train_samples, eval_samples=eval_samples
)

trainer.fit()