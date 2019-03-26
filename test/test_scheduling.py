import pytest
import multiprocessing
import time
import os


from CAT import record

# UTILITY FUNCTION

def run_forever(arg):
	while True:
		continue


# TESTS

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

	monkeypatch.setattr(record, "record", increment_recording_process_counter)
	
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

	monkeypatch.setattr(record, "analyze_audio_files", increment_analysis_process_counter)
	
	# start the Process creation function
	record.start_processes()

	# give the Processes plenty of time to start and increment their counters
	time.sleep(1)
	
	# check that the proper number of processes have been created
	assert recording_process_counter.value == 1
	assert analysis_process_counter.value == record.NUM_CORES - 1


def test_analyze_audio_files(monkeypatch):
	processed_files = multiprocessing.Queue()

	# replace the audio analysis function with placing the filename that would have been processed into a queue
	# also check that unused arguments are appropriate
	def analyze_audio_file_mock(filename, speaker_dictionary, speaker_dictionary_lock):
		assert type(speaker_dictionary) == multiprocessing.managers.DictProxy
		assert type(speaker_dictionary_lock) == multiprocessing.synchronize.Lock
		processed_files.put(filename)
	monkeypatch.setattr(record, "analyze_audio_file", analyze_audio_file_mock)

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
	process = multiprocessing.Process(target=record.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock))
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


def test_analyze_audio_files_late_add(monkeypatch):
	# replace the audio analysis function with placing the filename that would have been processed into a queue
	processed_files = multiprocessing.Queue()
	monkeypatch.setattr(record, "analyze_audio_file", lambda filename, _, __: processed_files.put(filename))

	# initialize an empty queue of files
	file_queue = multiprocessing.Queue()

	# other arguments for the processing threads
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = multiprocessing.Lock()

	# start the audio analysis Process
	process = multiprocessing.Process(target=record.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock))
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