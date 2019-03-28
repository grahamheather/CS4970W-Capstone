import pytest
import unittest.mock as mock
import multiprocessing
import time
import os

from CAT import settings

# file under test
from CAT import scheduling

# UTILITY FUNCTION

def run_forever(arg):
	while True:
		continue


# TESTS

# Test starting the recording and processing threads
def test_start_processes(monkeypatch):
	# replace the functioning of each process with incrementing a counter
	# to track how many of each kind of process are created
	
	# recording Processes
	global recording_process_counter
	recording_process_counter = multiprocessing.Value('i', 0)

	def increment_recording_process_counter(q):
		global recording_process_counter
		with recording_process_counter.get_lock():
			recording_process_counter.value += 1

	monkeypatch.setattr("CAT.scheduling.record.record", increment_recording_process_counter)
	
	# analysis Processes
	global analysis_process_counter
	analysis_process_counter = multiprocessing.Value('i', 0)

	def increment_analysis_process_counter(a, b, c):
		assert type(a) == multiprocessing.queues.Queue
		assert type(b) == multiprocessing.managers.DictProxy
		assert type(c) == multiprocessing.synchronize.Lock
		global analysis_process_counter
		with analysis_process_counter.get_lock():
			analysis_process_counter.value += 1

	monkeypatch.setattr(scheduling, "analyze_audio_files", increment_analysis_process_counter)
	
	# start the Process creation function
	scheduling.start_processes()

	# give the Processes plenty of time to start and increment their counters
	time.sleep(1)
	
	# check that the proper number of processes have been created
	assert recording_process_counter.value == 1
	assert analysis_process_counter.value == settings.NUM_CORES - 1


# Test analyzing audio files in processing queue
def test_analyze_audio_files(monkeypatch):
	processed_files = multiprocessing.Queue()

	# replace the audio analysis function with placing the filename that would have been processed into a queue
	# also check that unused arguments are appropriate
	def analyze_audio_file_mock(filename, speaker_dictionary, speaker_dictionary_lock):
		assert type(speaker_dictionary) == multiprocessing.managers.DictProxy
		assert type(speaker_dictionary_lock) == multiprocessing.synchronize.Lock
		processed_files.put(filename)
	monkeypatch.setattr(scheduling, "analyze_audio_file", analyze_audio_file_mock)

	# initialize a list of files to process
	file_queue = multiprocessing.Queue()
	filenames = ['abc.txt', 'test.wav', 'nothing.txt']
	for filename in filenames:
		# create each file
		file = open(filename, 'w')
		file.close()
		file_queue.put(filename)
		# check that file creation was sucessful
		assert os.path.isfile(filename)

	# check that all filenames were successfully placed in the queue
	assert file_queue.qsize() == len(filenames)

	# other arguments for the processing threads
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = multiprocessing.Lock()

	# start the audio analysis Process
	process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock))
	process.start()

	# give the Process sufficient time to iterate over all files
	time.sleep(1)

	# end the Process (otherwise it will loop infinitely)
	process.terminate()

	# check that all files were processed
	assert file_queue.qsize() == 0
	
	# check that the audio analysis function was called on every file
	assert processed_files.qsize() == len(filenames)
	while not processed_files.empty():
		assert processed_files.get() in filenames

	# check that all files were ultimately deleted
	for filename in filenames:
		assert not os.path.isfile(filename)


# Test analyzing a new audio file added to the processing queue
def test_analyze_audio_files_late_add(monkeypatch):
	# replace the audio analysis function with placing the filename that would have been processed into a queue
	processed_files = multiprocessing.Queue()
	monkeypatch.setattr(scheduling, "analyze_audio_file", lambda filename, _, __: processed_files.put(filename))

	# initialize an empty queue of files
	file_queue = multiprocessing.Queue()

	# other arguments for the processing threads
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = multiprocessing.Lock()

	# start the audio analysis Process
	process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock))
	process.start()

	# wait a small amount of time
	time.sleep(.5)

	# now add files to the queue
	filenames = ['abc.txt', 'test.wav', 'nothing.txt']
	for filename in filenames:
		# create each file
		file = open(filename, 'w')
		file.close()
		# check that file creation was sucessful
		assert os.path.isfile(filename)
		# add the file to the queue
		file_queue.put(filename)

	# give the Process sufficient time to iterate over all files
	time.sleep(.5)

	# end the Process (otherwise it will loop infinitely)
	process.terminate()

	# check that all files were processed
	assert file_queue.qsize() == 0
	
	# check that the audio analysis function was called on every file
	assert processed_files.qsize() == len(filenames)
	while not processed_files.empty():
		assert processed_files.get() in filenames

	# check that all files were ultimately deleted
	for filename in filenames:
		assert not os.path.isfile(filename)


# Test that audio file analysis calls extracts features and transmits (with speaker diarization)
@mock.patch('CAT.scheduling.os.remove')
@mock.patch('CAT.scheduling.transmission.transmit')
@mock.patch('CAT.scheduling.feature_extraction.extract_features')
@mock.patch('CAT.scheduling.speaker_id.identify_speakers')
def test_analyze_audio_file_speaker_diarization(identify_speakers_mock, extract_features_mock, transmit_mock, remove_mock):
	# enable speaker diarization
	scheduling.SPEAKER_DIARIZATION = True

	# initialize mock return values
	identify_speakers_mock.return_value=[('file1.wav', 'speaker1'), ('file2.wav', 'speaker2')]
	extract_features_mock.side_effect = [[1, 2, 3, 4], [5, 6, 7, 8]]
	
	# call function
	dictionary = {}
	lock = multiprocessing.Lock()
	scheduling.analyze_audio_file('test_file.wav', dictionary, lock)
	
	# test identify_speakers called properly
	identify_speakers_mock.assert_called_once_with('test_file.wav', dictionary, lock)
	
	# test extract_features called properly
	assert extract_features_mock.call_count == 2
	extract_features_mock.assert_has_calls([mock.call('file1.wav'), mock.call('file2.wav')])

	# test transmit called properly
	assert transmit_mock.call_count == 2
	transmit_mock.assert_has_calls([
		mock.call([1, 2, 3, 4], 'speaker1'),
		mock.call([5, 6, 7, 8], 'speaker2')
	])

	# test files removed properly
	assert remove_mock.call_count == 2
	remove_mock.assert_has_calls([
		mock.call('file1.wav'),
		mock.call('file2.wav')
	])


# Test that audio file analysis extracts features and transmits (without speaker diarization)
@mock.patch('CAT.scheduling.os.remove')
@mock.patch('CAT.scheduling.transmission.transmit')
@mock.patch('CAT.scheduling.feature_extraction.extract_features')
@mock.patch('CAT.scheduling.speaker_id.identify_speakers')
def test_analyze_audio_file_no_speaker_diarization(identify_speakers_mock, extract_features_mock, transmit_mock, remove_mock):
	# disable speaker diarization
	scheduling.SPEAKER_DIARIZATION = False

	# initialize mock return values
	identify_speakers_mock.return_value=[('file1.wav', 'speaker1'), ('file2.wav', 'speaker2')]
	extract_features_mock.side_effect = [[1, 2, 3, 4], [5, 6, 7, 8]]
	
	# call function
	dictionary = {}
	lock = multiprocessing.Lock()
	scheduling.analyze_audio_file('test_file.wav', dictionary, lock)
	
	# test identify_speakers called properly
	identify_speakers_mock.assert_not_called()
	
	# test extract_features called properly
	extract_features_mock.assert_called_once_with('test_file.wav')

	# test transmit called properly
	transmit_mock.assert_called_once_with([1, 2, 3, 4], None)

	# test that no additional files were removed
	remove_mock.assert_not_called()