import pytest
import unittest.mock as mock

# supporting libraries
from os import path
import numpy
import multiprocessing
import datetime

from CAT import settings

# file under test
from CAT import speaker_reid


# UTILITY FUNCTIONS

def get_test_recording_dir():
	return path.join('test', 'test_recordings')


# FIXTURES

@pytest.fixture()
def config():
	return settings.Config()


# TESTS

# test that distance between two identical speakers is 0
def test_speaker_distance_same():
	mean = numpy.array([[1], [0], [0]])
	covariance = numpy.array([[1, 6, 0],
							 [6, 4, 1],
							 [0, 1, 4]
							 ])
	result = speaker_reid.speaker_distance(mean, covariance, mean, covariance)
	assert result == 0


# test distance an arbitrary pair of speakers
# CURRENTLY EUCLIDEAN DISTANCE
def test_speaker_distance_valid():
	mean1 = numpy.array([[1], [0]])
	mean0 = numpy.array([[2], [0]])
	covariance1 = [[1, 0], [0, 1]]
	covariance0 = [[2, .5], [.5, 2]]
	result = speaker_reid.speaker_distance(mean0, covariance0, mean1, covariance1)
	assert abs(result - 1) < .00001


# test a singular matrix does not cause an error
def test_speaker_distance_singlar():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 2],
							  [2, 4]
							 ])
	result = speaker_reid.speaker_distance(mean, covariance, mean, covariance)


# test that a new speaker can be added with no previous speakers
@mock.patch("CAT.speaker_reid.transmission.register_speaker")
def test_identify_speaker_empty(new_speaker_mock, config):
	# initialize mock
	new_speaker_mock.return_value = "test_speaker"

	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert result == "test_speaker"
	assert len(dictionary) == 1
	assert result in dictionary
	assert (dictionary[result]["mean"] == mean).all()
	assert (dictionary[result]["covariance"] == covariance).all()
	assert dictionary[result]["count"] == 1
	assert dictionary[result]["last_seen"] - datetime.datetime.now() < datetime.timedelta(hours=1)


# test that a speaker can be compared against previous speakers\
@mock.patch("CAT.speaker_reid.transmission.update_speaker")
def test_identify_speaker_previous(update_speaker_mock, config):
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1.5], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		},
		'xyz': {
			"mean": numpy.array([[5], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert len(dictionary) == 2
	assert result == 'abc'
	assert len(dictionary[result]) == 4
	assert (dictionary[result]["mean"] == numpy.array([[1.375], [0]])).all()
	assert (dictionary[result]["covariance"] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result]["count"] == 4
	assert dictionary[result]["last_seen"] - datetime.datetime.now() < datetime.timedelta(hours=1)
	assert update_speaker_mock.call_args[0][0] == config
	assert update_speaker_mock.call_args[0][1] == 'abc'
	assert (update_speaker_mock.call_args[0][2] == numpy.array([[1.375], [0]])).all()
	assert (update_speaker_mock.call_args[0][3] == numpy.array([[1, 0], [0, 1]])).all()
	assert update_speaker_mock.call_args[0][4] == 4


# test that a speaker can be compared against previous speakers
# including ones with singular matrices
@mock.patch("CAT.speaker_reid.transmission.update_speaker")
def test_identify_speaker_invalid_previous(update_speaker_mock, config):
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1.5], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		},
		'xyz': {
			"mean": numpy.array([[1.5], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert len(dictionary) == 2
	assert result == 'abc'
	assert len(dictionary[result]) == 4
	assert (dictionary[result]["mean"] == numpy.array([[1.375], [0]])).all()
	assert (dictionary[result]["covariance"] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result]["count"] == 4
	assert dictionary[result]["last_seen"] - datetime.datetime.now() < datetime.timedelta(hours=1)
	update_speaker_mock.assert_called_once()
	assert update_speaker_mock.call_args[0][0] == config
	assert update_speaker_mock.call_args[0][1] == 'abc'
	assert (update_speaker_mock.call_args[0][2] == numpy.array([[1.375], [0]])).all()
	assert (update_speaker_mock.call_args[0][3] == numpy.array([[1, 0], [0, 1]])).all()
	assert update_speaker_mock.call_args[0][4] == 4


# test that a new speaker can be identified from previous speakers
# including ones with singular matrices
@mock.patch("CAT.speaker_reid.transmission.register_speaker")
def test_identify_speaker_new(new_speaker_mock, config):
	# initialize mock
	new_speaker_mock.return_value = 'test_speaker'

	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		},
		'xyz': {
			"mean": numpy.array([[-1000000000], [0]]),
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert len(dictionary) == 3
	assert result == 'test_speaker'
	assert len(dictionary[result]) == 4
	assert (dictionary[result]["mean"] == numpy.array([[1], [0]])).all()
	assert (dictionary[result]["covariance"] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result]["count"] == 1
	assert dictionary[result]["last_seen"] - datetime.datetime.now() < datetime.timedelta(hours=1)


# test that a new speaker can be identified from previous speakers
# including ones with singular matrices
@mock.patch("CAT.speaker_reid.transmission.register_speaker")
def test_identify_speaker_invalid_new(new_speaker_mock, config):
	# initialize mock
	new_speaker_mock.return_value = 'test_speaker'

	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		},
		'xyz': {
			"mean": numpy.array([[-100000000], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now() - datetime.timedelta(weeks=1)
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert len(dictionary) == 3
	assert (not result == 'abc') and (not result == 'xyz')
	assert len(dictionary[result]) == 4
	assert (dictionary[result]["mean"] == numpy.array([[1], [0]])).all()
	assert (dictionary[result]["covariance"] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result]["count"] == 1
	assert dictionary[result]["last_seen"] - datetime.datetime.now() < datetime.timedelta(hours=1)


# test that speakers are eventually forgotten
@mock.patch("CAT.speaker_reid.transmission.delete_speaker")
@mock.patch("CAT.speaker_reid.transmission.register_speaker")
def test_identify_speakers_forget_speakers(new_speaker_mock, delete_speaker_mock, config):
	# initialize mock
	new_speaker_mock.return_value = "test_speaker"

	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now()
		},
		'a1b2c3': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now() - config.get("speaker_forget_interval")
		},
		'xyz': {
			"mean": numpy.array([[-100000000], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now()
		},
		'x1y2z3': {
			"mean": numpy.array([[-100000000], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now() - 2 * config.get("speaker_forget_interval")
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config)
	assert 'abc' in dictionary
	assert 'xyz' in dictionary
	assert 'a1b2c3' not in dictionary
	assert 'x1y2z3' not in dictionary
	assert delete_speaker_mock.call_count == 2
	delete_speaker_mock.assert_any_call(config, 'a1b2c3')
	delete_speaker_mock.assert_any_call(config, 'x1y2z3')


# test that speakers are eliminated if there are too many
@mock.patch("CAT.speaker_reid.transmission.delete_speaker")
@mock.patch("CAT.speaker_reid.transmission.register_speaker")
def test_identify_speakers_too_many_speakers(new_speaker_mock, delete_speaker_mock, config):
	# initialize mock
	new_speaker_mock.return_value = "test_speaker"

	# lower maximum number of speakers
	def mock_max_speakers(key):
		if key == "max_number_of_speakers":
			return 2
		else:
			return config.get(key)

	config_mock = mock.Mock()
	config_mock.get = mock_max_speakers

	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 1,
			"last_seen": datetime.datetime.now()
		},
		'a1b2c3': {
			"mean": numpy.array([[1000000000], [0]]), 
			"covariance": numpy.array([[1, 0], [0, 1]]), 
			"count": 3,
			"last_seen": datetime.datetime.now()
		},
		'xyz': {
			"mean": numpy.array([[-100000000], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 1,
			"last_seen": datetime.datetime.now()
		},
		'x1y2z3': {
			"mean": numpy.array([[-100000000], [0]]),
			"covariance": numpy.array([[1, 1], [1, 1]]), 
			"count": 5,
			"last_seen": datetime.datetime.now()
		}
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock, config_mock)
	assert 'abc' not in dictionary
	assert 'xyz' not in dictionary
	assert 'a1b2c3' in dictionary
	assert 'x1y2z3' in dictionary
	assert delete_speaker_mock.call_count == 3
	delete_speaker_mock.assert_any_call(config_mock, 'abc')
	delete_speaker_mock.assert_any_call(config_mock, 'xyz')
	delete_speaker_mock.assert_any_call(config_mock, 'test_speaker')