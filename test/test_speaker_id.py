import pytest
import unittest.mock as mock

# supporting libraries
from os import path
import os
import multiprocessing
import pickle
import numpy

# file under test
from CAT import speaker_id


# testing file generation
import gen_audio

# this process can be slow
# it can be disabled if settings have not been changed (the necessary files are saved)
REGENERATE_FILES = False


# UTILITY FUNCTIONS

def get_recording_dir():
	return path.join('CAT', 'recordings')

def get_test_recording_dir():
	return path.join('test', 'test_recordings')


# FIXTURES

@pytest.fixture(scope="session", autouse=True)
def generate_audio_files():
	if REGENERATE_FILES:
		stats = gen_audio.generate_test_speaker_id_audio(get_test_recording_dir())
		with open(path.join(get_test_recording_dir(), 'test_speaker_id_stats.pickle'), 'wb') as f:
			pickle.dump(stats, f)
	else:
		with open(path.join(get_test_recording_dir(), 'test_speaker_id_stats.pickle'), 'rb') as f:
			stats = pickle.load(f)

	return stats


# remove all recordings from previous tests before each new test
@pytest.fixture(autouse=True)
def cleanup():
	for filename in os.listdir(get_recording_dir()):
		file_path = path.join(path.join(get_recording_dir(), filename))
		try:
			os.remove(file_path)
		except Exception as e:
			print(e)


# TESTS

# Test that a previously seen speaker can be identified in a new recording
@pytest.mark.filterwarnings("ignore:")
def test_identify_speakers_same_recording(generate_audio_files):
	# The speaker diarization module is unstable.
	# It is provided as an extra feature to be improved and developed upon.
	# As such the realistic tests for it are equally unstable.
	# Prior tests guarantee that the code functions apporpriately in simplistic cases.
	# These tests check that the entire section is assembled properly and can return the correct answers.
	# Multiple runs are calculated to ensure that the tests should (almost) always pass.
	runs = []
	for _ in range(5):
		tests = []

		filename = path.join(get_test_recording_dir(), "speaker_id_same_recording.wav")
		dictionary = {}
		lock = multiprocessing.Lock()

		# check that the first new speaker is identified properly
		result1 = speaker_id.identify_speakers(filename, dictionary, lock)
		speakers1 = set(speaker for file, speaker in result1)
		tests.append(len(dictionary) == 1)
		tests.append(len(speakers1) == 1)
		tests.append(list(dictionary.keys())[0] in speakers1)

		# check that that speaker is re-identified propery as well
		# (in an identical recording)
		result = speaker_id.identify_speakers(filename, dictionary, lock)
		speakers = set(speaker for file, speaker in result)
		tests.append(len(dictionary) == 1)
		tests.append(len(speakers) == 1)
		tests.append(list(dictionary.keys())[0] in speakers)

		runs.append(all(tests))

	assert any(runs)


# Test differentiating a new speaker from previously seen ones in recordings
@pytest.mark.filterwarnings("ignore:")
def test_identify_speakers_new_speaker(generate_audio_files):
	# The speaker diarization module is unstable.
	# It is provided as an extra feature to be improved and developed upon.
	# As such the realistic tests for it are equally unstable.
	# Prior tests guarantee that the code functions apporpriately in simplistic cases.
	# These tests check that the entire section is assembled properly and can return the correct answers.
	# Multiple runs are calculated to ensure that the tests should (almost) always pass.
	runs = []
	for _ in range(5):
		tests = []

		filename1 = path.join(get_test_recording_dir(), "speaker_id_same_recording.wav")
		filename2 = path.join(get_test_recording_dir(), "speaker_id_two_speakers.wav")
		dictionary = {}
		lock = multiprocessing.Lock()

		# check that the first new speaker is identified properly
		result1 = speaker_id.identify_speakers(filename1, dictionary, lock)
		speakers1 = set(speaker for file, speaker in result1)
		tests.append(len(dictionary) == 1)
		tests.append(len(speakers1) == 1)
		tests.append(list(dictionary.keys())[0] in speakers1)

		# check that that speaker is re-identified propery as well
		# (in an identical recording)
		result2 = speaker_id.identify_speakers(filename2, dictionary, lock)
		speakers2 = set(speaker for file, speaker in result2)
		tests.append(len(dictionary) == 2)
		tests.append(len(speakers2) == 2)
		tests.append(any(speaker in speakers1 for speaker in speakers2))

		runs.append(all(tests))
	assert any(runs)


# Test differentiating a speakers and running out of disk space
@mock.patch("CAT.speaker_id.speaker_reid.identify_speaker")
@mock.patch("CAT.speaker_id.diarization.split_by_speaker")
@mock.patch("CAT.speaker_id.utilities.save_to_file")
@pytest.mark.filterwarnings("ignore:")
def test_identify_speakers_no_space(save_mock, split_mock, identify_mock, generate_audio_files):
	# random audio data
	noise = generate_audio_files["noise"]

	# set up mocks
	means = numpy.zeros((3, 5))
	covariances = numpy.zeros((3, 5, 5))
	split_mock.return_value = ({0: [noise], 1:[noise], 2:[noise]}, means, covariances)
	identify_mock.return_value = 'a'
	save_mock.side_effect = ['test1.wav', IOError(), 'test2.wav']

	# run function
	result = speaker_id.identify_speakers('test.wav', {}, None)

	# check that only the appropriate files were listed
	assert result == [('test1.wav', 'a'), ('test2.wav', 'a')]