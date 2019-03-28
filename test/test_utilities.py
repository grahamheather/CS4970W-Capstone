import pytest
import unittest.mock as mock

# supporting libraries
from os import path
import os
import pickle

from CAT.settings import *

# file under test
from CAT import utilities

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
		stats = gen_audio.generate_test_utilities_audio(get_test_recording_dir())
		with open(path.join(get_test_recording_dir(), 'test_utilities_stats.pickle'), 'wb') as f:
			pickle.dump(stats, f)
	else:
		with open(path.join(get_test_recording_dir(), 'test_utilities_stats.pickle'), 'rb') as f:
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

# test reading an audio file
def test_read_file_exists(generate_audio_files):
	# test reading the file
	result1 = utilities.read_file(path.join(get_test_recording_dir(), 'utilities_read_file.wav'))
	data = generate_audio_files['read_file']
	assert data == result1

	# test reading the file again, to be sure it has not been corrupted
	result2 = utilities.read_file(path.join(get_test_recording_dir(), 'utilities_read_file.wav'))
	assert data == result2


# test that attempting to read a missing file is handled
def test_read_file_not_exists():
	result = utilities.read_file(path.join(get_test_recording_dir(), 'read_file_not_exists.wav'))
	assert result == b''


# test that a file can be written
def test_save_to_file(generate_audio_files):
	data = generate_audio_files['read_file']
	result = utilities.save_to_file(data)
	written_data = utilities.read_file(result)
	assert data == written_data


# test that a file is not written with the disk is almost full
@mock.patch("CAT.utilities.shutil.disk_usage")
def test_save_to_file_no_space(usage_mock, generate_audio_files):
	usage_mock.return_value = (MIN_EMPTY_SPACE_IN_BYTES * 2,  MIN_EMPTY_SPACE_IN_BYTES + 1, MIN_EMPTY_SPACE_IN_BYTES - 1)
	data = generate_audio_files['read_file']
	with pytest.raises(IOError):
		result = utilities.save_to_file(data)
	assert len(os.listdir(get_recording_dir())) == 0

