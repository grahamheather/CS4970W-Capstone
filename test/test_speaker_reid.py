import pytest

# supporting libraries
from os import path
import numpy
import multiprocessing

# file under test
from CAT import speaker_reid


# UTILITY FUNCTIONS

def get_test_recording_dir():
	return path.join('test', 'test_recordings')


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
def test_identify_speaker_empty():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock)
	assert len(dictionary) == 1
	assert result in dictionary
	assert dictionary[result] == (mean, covariance, 1)


# test that a speaker can be compared against previous speakers
def test_identify_speaker_previous():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': (
			numpy.array([[1.5], [0]]), 
			numpy.array([[1, 0], [0, 1]]), 
			3
		),
		'xyz': (
			numpy.array([[5], [0]]), 
			numpy.array([[1, 0], [0, 1]]), 
			3
		)
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock)
	assert len(dictionary) == 2
	assert result == 'abc'
	assert len(dictionary[result]) == 3
	assert (dictionary[result][0] == numpy.array([[1.375], [0]])).all()
	assert (dictionary[result][1] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result][2] == 4


# test that a speaker can be compared against previous speakers
# including ones with singular matrices
def test_identify_speaker_invalid_previous():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': (
			numpy.array([[1.5], [0]]), 
			numpy.array([[1, 0], [0, 1]]), 
			3),
		'xyz': (
			numpy.array([[1.5], [0]]),
			numpy.array([[1, 1], [1, 1]]), 
			5
		)
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock)
	assert len(dictionary) == 2
	assert result == 'abc'
	assert len(dictionary[result]) == 3
	assert (dictionary[result][0] == numpy.array([[1.375], [0]])).all()
	assert (dictionary[result][1] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result][2] == 4


# te that a new speaker can be identified from previous speakers
# including ones with singular matrices
def test_identify_speaker_new():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': (
			numpy.array([[1000000000], [0]]), 
			numpy.array([[1, 0], [0, 1]]), 
			3),
		'xyz': (
			numpy.array([[-1000000000], [0]]),
			numpy.array([[1, 0], [0, 1]]), 
			5
		)
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock)
	assert len(dictionary) == 3
	assert (not result == 'abc') and (not result == 'xyz')
	assert len(dictionary[result]) == 3
	assert (dictionary[result][0] == numpy.array([[1], [0]])).all()
	assert (dictionary[result][1] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result][2] == 1


# test that a new speaker can be identified from previous speakers
# including ones with singular matrices	
def test_identify_speaker_invalid_new():
	mean = numpy.array([[1], [0]])
	covariance = numpy.array([[1, 0], [0, 1]])
	dictionary = {
		'abc': (
			numpy.array([[1000000000], [0]]), 
			numpy.array([[1, 0], [0, 1]]), 
			3
		),
		'xyz': (
			numpy.array([[-100000000], [0]]),
			numpy.array([[1, 1], [1, 1]]), 
			5
		)
	}
	lock = multiprocessing.Lock()
	result = speaker_reid.identify_speaker(mean, covariance, dictionary, lock)
	assert len(dictionary) == 3
	assert (not result == 'abc') and (not result == 'xyz')
	assert len(dictionary[result]) == 3
	assert (dictionary[result][0] == numpy.array([[1], [0]])).all()
	assert (dictionary[result][1] == numpy.array([[1, 0], [0, 1]])).all()
	assert dictionary[result][2] == 1