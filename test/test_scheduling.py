import pytest
import unittest.mock as mock

# supporting libraries
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


# FIXTURES

@pytest.fixture()
def config():
	return settings.Config()


# TESTS

# Test starting the recording and processing threads
@mock.patch("CAT.scheduling.transmission.register_device")
@mock.patch("CAT.scheduling.transmission.get_speakers")
def test_start_processes(get_speakers_mock, register_device_mock, monkeypatch, config):
	# initialize mock
	get_speakers_mock.return_value = {'test_speaker': []}

	# replace the functioning of each process with incrementing a counter
	# to track how many of each kind of process are created
	
	# recording Processes
	global recording_process_counter
	recording_process_counter = multiprocessing.Value('i', 0)

	def increment_recording_process_counter(q, c, s, e):
		assert type(q) == multiprocessing.queues.Queue
		assert str(type(c)) == "<class 'multiprocessing.managers.AutoProxy[Config]'>" # type isn't registered yet
		assert type(s) == multiprocessing.synchronize.Semaphore
		assert type(e) == multiprocessing.synchronize.Event
		global recording_process_counter
		with recording_process_counter.get_lock():
			recording_process_counter.value += 1

	monkeypatch.setattr("CAT.scheduling.record.record", increment_recording_process_counter)
	
	# analysis Processes
	global analysis_process_counter
	analysis_process_counter = multiprocessing.Value('i', 0)

	def increment_analysis_process_counter(q, d, l, c, s, e, l2):
		assert type(q) == multiprocessing.queues.Queue
		assert type(d) == multiprocessing.managers.DictProxy
		assert 'test_speaker' in d
		assert type(l) == multiprocessing.synchronize.Lock
		assert str(type(c)) == "<class 'multiprocessing.managers.AutoProxy[Config]'>" # type isn't registered yet
		assert type(s) == multiprocessing.synchronize.Semaphore
		assert type(e) == multiprocessing.synchronize.Event
		assert type(l2) == multiprocessing.synchronize.Lock
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
	assert analysis_process_counter.value == config.get("num_cores") - 1

	# check that speakers were queried
	get_speakers_mock.assert_called_once()

	# check that the device was registered
	register_device_mock.assert_called_once()


# Test analyzing audio files in processing queue
def test_analyze_audio_files(monkeypatch, config):
	# initialize Process-shared objects
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = multiprocessing.Lock()
	semaphore = multiprocessing.Semaphore(1)
	event = multiprocessing.Event()
	event.set()
	lock = multiprocessing.Lock()

	# replace the audio analysis function with placing the filename that would have been processed into a queue
	# also check that unused arguments are appropriate
	processed_files = multiprocessing.Queue()
	def analyze_audio_file_mock(filename, speaker_dictionary, speaker_dictionary_lock, config):
		assert type(speaker_dictionary) == multiprocessing.managers.DictProxy
		assert type(speaker_dictionary_lock) == multiprocessing.synchronize.Lock
		assert type(config) == settings.Config
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

	# start the audio analysis Process
	process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(
		file_queue, speaker_dictionary, speaker_dictionary_lock, config, semaphore, event, lock))
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
def test_analyze_audio_files_late_add(monkeypatch, config):
	# initialized Process-shared objects
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = multiprocessing.Lock()
	semaphore = multiprocessing.Semaphore(1)
	event = multiprocessing.Event()
	event.set()
	lock = multiprocessing.Lock()

	# replace the audio analysis function with placing the filename that would have been processed into a queue
	processed_files = multiprocessing.Queue()
	monkeypatch.setattr(scheduling, "analyze_audio_file", lambda filename, _, __, ___: processed_files.put(filename))

	# initialize an empty queue of files
	file_queue = multiprocessing.Queue()

	# start the audio analysis Process
	process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(
		file_queue, speaker_dictionary, speaker_dictionary_lock, config, semaphore, event, lock))
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
	config_mock = mock.Mock()
	config_mock.get.return_value = True

	# initialize mock return values
	identify_speakers_mock.return_value=[('file1.wav', 'speaker1'), ('file2.wav', 'speaker2')]
	extract_features_mock.side_effect = [[1, 2, 3, 4], [5, 6, 7, 8]]
	
	# call function
	dictionary = {}
	lock = multiprocessing.Lock()
	scheduling.analyze_audio_file('test_file.wav', dictionary, lock, config_mock)
	
	# test identify_speakers called properly
	identify_speakers_mock.assert_called_once_with('test_file.wav', dictionary, lock, config_mock)
	
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


# test that audio file analysis extracts features and transmits (without speaker diarization)
@mock.patch('CAT.scheduling.os.remove')
@mock.patch('CAT.scheduling.transmission.transmit')
@mock.patch('CAT.scheduling.feature_extraction.extract_features')
@mock.patch('CAT.scheduling.speaker_id.identify_speakers')
def test_analyze_audio_file_no_speaker_diarization(identify_speakers_mock, extract_features_mock, transmit_mock, remove_mock, config):
	# disable speaker diarization
	# enable speaker diarization
	config_mock = mock.Mock()
	config_mock.get.return_value = False

	# initialize mock return values
	identify_speakers_mock.return_value=[('file1.wav', 'speaker1'), ('file2.wav', 'speaker2')]
	extract_features_mock.side_effect = [[1, 2, 3, 4], [5, 6, 7, 8]]
	
	# call function
	dictionary = {}
	lock = multiprocessing.Lock()
	scheduling.analyze_audio_file('test_file.wav', dictionary, lock, config_mock)
	
	# test identify_speakers called properly
	identify_speakers_mock.assert_not_called()
	
	# test extract_features called properly
	extract_features_mock.assert_called_once_with('test_file.wav')

	# test transmit called properly
	transmit_mock.assert_called_once_with([1, 2, 3, 4], None)

	# test that no additional files were removed
	remove_mock.assert_not_called()