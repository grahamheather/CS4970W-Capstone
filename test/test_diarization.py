import pytest

# supporting libraries
from os import path
import pickle
import wave

from CAT import settings

# file under test
from CAT import diarization

# testing file generation
import gen_audio

# this process can be slow
# it can be disabled if settings have not been changed (the necessary files are saved)
REGENERATE_FILES = False
NUMBER_OF_FEATURES = 26

# UTILITY FUNCTIONS

def get_test_recording_dir():
	return path.join('test', 'test_recordings')

def read_wav(filename):
	wave_file = wave.open(filename, 'r')
	return wave_file.readframes(wave_file.getnframes())


# FIXTURES

@pytest.fixture(scope="session", autouse=True)
def generate_audio_files():
	if REGENERATE_FILES:
		stats = gen_audio.generate_test_diarization_audio(get_test_recording_dir())
		with open(path.join(get_test_recording_dir(), 'test_diarization_stats.pickle'), 'wb') as f:
			pickle.dump(stats, f)
	else:
		with open(path.join(get_test_recording_dir(), 'test_diarization_stats.pickle'), 'rb') as f:
			stats = pickle.load(f)

	return stats

@pytest.fixture()
def config():
	return settings.Config()



# TESTS

# test separating 2 different speakers
# ignore warnings generated by pyAudioAnalysis
@pytest.mark.filterwarnings("ignore:")
def test_split_by_speaker_normal(generate_audio_files, config):
	result, means, covariances = diarization.split_by_speaker(path.join(get_test_recording_dir(), "diarization_normal.wav"), config)

	# check valid shape output of parameters
	assert means.shape[0] == covariances.shape[0]
	assert means.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[2] == NUMBER_OF_FEATURES
	assert max(result.keys()) <= means.shape[0]

	valid_speakers = [speaker for speaker in result if len(result[speaker]) > 0]
	assert len(valid_speakers) == 2
	
	assert len(result[valid_speakers[0]]) == 1
	assert len(result[valid_speakers[1]]) == 1

	segment1 = result[valid_speakers[0]][0]
	segment2 = result[valid_speakers[1]][0]

	audio = read_wav(path.join(get_test_recording_dir(), "diarization_normal.wav"))
	(start1, end1), (start2, end2) = generate_audio_files["normal"]
	desired_speech1 = audio[start1 + 15000:end1 - 15000]
	desired_speech2 = audio[start2 + 15000:end2 - 15000]

	if desired_speech1 in segment1:
		assert desired_speech2 in segment2
	else:
		assert desired_speech1 in segment2
		assert desired_speech2 in segment1


# test separating 2 different speakers with the addition of background noise
# ignore warnings generated by pyAudioAnalysis
@pytest.mark.filterwarnings("ignore:")
def test_split_by_speaker_noise(generate_audio_files, config):
	result, means, covariances = diarization.split_by_speaker(path.join(get_test_recording_dir(), "diarization_noise.wav"), config)
	
	# check valid shape output of parameter
	assert means.shape[0] == covariances.shape[0]
	assert means.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[2] == NUMBER_OF_FEATURES
	assert max(result.keys()) <= means.shape[0]

	valid_speakers = [speaker for speaker in result if len(result[speaker]) > 0]
	assert len(valid_speakers) == 2
	
	assert len(result[valid_speakers[0]]) == 1
	assert len(result[valid_speakers[1]]) == 1

	segment1 = result[valid_speakers[0]][0]
	segment2 = result[valid_speakers[1]][0]

	audio = read_wav(path.join(get_test_recording_dir(), "diarization_noise.wav"))
	(start1, end1), (start2, end2) = generate_audio_files["noise"]
	desired_speech1 = audio[start1 + 20000:end1 - 20000]
	desired_speech2 = audio[start2 + 20000:end2 - 20000]
	
	if desired_speech1 in segment1:
		assert desired_speech2 in segment2
	else:
		assert desired_speech1 in segment2
		assert desired_speech2 in segment1


# test not separating 1 speaker
# ignore warnings generated by pyAudioAnalysis
@pytest.mark.filterwarnings("ignore:")
def test_split_by_speaker_single(generate_audio_files, config):
	result, means, covariances = diarization.split_by_speaker(path.join(get_test_recording_dir(), "diarization_single.wav"), config)
	
	# check valid shape output of parameters
	assert means.shape[0] == covariances.shape[0]
	assert means.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[2] == NUMBER_OF_FEATURES
	assert max(result.keys()) <= means.shape[0]

	valid_speakers = [speaker for speaker in result if len(result[speaker]) > 0]
	assert len(valid_speakers) == 1
	
	assert len(result[valid_speakers[0]]) == 1

	segment = result[valid_speakers[0]][0]

	audio = read_wav(path.join(get_test_recording_dir(), "diarization_single.wav"))
	start, end = generate_audio_files["single"]
	desired_speech = audio[start + 10000:end - 10000]

	assert desired_speech in segment



# test not separating 1 speaker with the addition of background noise
# ignore warnings generated by pyAudioAnalysis
@pytest.mark.filterwarnings("ignore:")
def test_split_by_speaker_single_noise(generate_audio_files, config):
	result, means, covariances = diarization.split_by_speaker(path.join(get_test_recording_dir(), "diarization_single_noise.wav"), config)
	
	# check valid shape output of parameters
	assert means.shape[0] == covariances.shape[0]
	assert means.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[1] == NUMBER_OF_FEATURES
	assert covariances.shape[2] == NUMBER_OF_FEATURES
	assert max(result.keys()) <= means.shape[0]

	valid_speakers = [speaker for speaker in result if len(result[speaker]) > 0]
	assert len(valid_speakers) == 1
	
	assert len(result[valid_speakers[0]]) == 1

	segment = result[valid_speakers[0]][0]

	audio = read_wav(path.join(get_test_recording_dir(), "diarization_single_noise.wav"))
	start, end = generate_audio_files["single_noise"]
	desired_speech = audio[start + 10000:end - 10000]

	assert desired_speech in segment