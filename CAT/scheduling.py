# multiprocessing avoids Python's Global Interpreter Lock which
# prevents more than one thread running at a time.
# This allows the program to, ideally, take advantage of multiple
# cores on the Raspberry Pi.
from multiprocessing import Process, Queue, Manager, Value, Lock, Array

import os

from CAT import record
from CAT import speaker_id
from CAT import feature_extraction
from CAT import transmission
from CAT.settings import *


def analyze_audio_file(filename, speaker_dictionary, speaker_dictionary_lock):
	''' Analyzes the file of audio, extracting and processing speech

		Parameters:
			filename
				str, the name of the file to analyze
			speaker_dictionary
				dict, dictionary to store statistics about each speaker in
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently

	'''

	# files to analyze
	if SPEAKER_DIARIZATION:
		files = speaker_id.identify_speakers(filename, speaker_dictionary, speaker_dictionary_lock)
	else:
		files = [(filename, None)]

	# extract features and transmit
	for filename, speaker in files:
		features = feature_extraction.extract_features(filename)
		transmission.transmit(features, speaker)
		
		# if speaker diarization was used, new subfiles have been created and need to be removed
		if SPEAKER_DIARIZATION:
			os.remove(filename)


def analyze_audio_files(file_queue, speaker_dictionary, speaker_dictionary_lock):
	''' Analyzes files of audio extracting and processing speech

		Parameters:
			file_queue
				queue to get filenames from
			speaker_dictionary
				dictionary to store statistics about each speaker in
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently
	'''

	# analysis processes process files indefinitely
	while True:

		# block until a file is available in the queue
		filename = file_queue.get()
		
		# process the file
		analyze_audio_file(filename, speaker_dictionary, speaker_dictionary_lock)

		# delete the file
		os.remove(filename)


def start_processes():
	''' Starts all process of the program '''

	process_manager = Manager()
	speaker_dictionary = process_manager.dict()
	speaker_dictionary_lock = Lock()
	file_queue = Queue() # thread-safe FIFO queue

	# ideally of the cores should run the record.recording process
	# and the other cores will run the analysis processes
	record.recording_process = Process(target=record.record, args=(file_queue,))
	record.recording_process.start()
	analysis_processes = [Process(target=analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock)) for _ in range(NUM_CORES - 1)]
	for process in analysis_processes:
		process.start()

	# block until the record.recording process exits (never, unless error)
	record.recording_process.join()


if __name__ == '__main__':
	start_processes()