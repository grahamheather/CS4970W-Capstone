# multiprocessing avoids Python's Global Interpreter Lock which
# prevents more than one thread running at a time.
# This allows the program to, ideally, take advantage of multiple
# cores on the Raspberry Pi.
from multiprocessing import Process, Queue, Manager, Value, Lock, Array, Event, Semaphore

import os

from CAT import record
from CAT import speaker_id
from CAT import feature_extraction
from CAT import transmission
from CAT import settings


def analyze_audio_file(filename, speaker_dictionary, speaker_dictionary_lock, config):
	''' Analyzes the file of audio, extracting and processing speech

		Parameters:
			filename
				str, the name of the file to analyze
			speaker_dictionary
				dict, dictionary to store statistics about each speaker in
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently
			config
				CAT.settings.Config - all settings associated with the program

	'''

	# files to analyze
	if config.get("speaker_diarization"):
		files = speaker_id.identify_speakers(filename, speaker_dictionary, speaker_dictionary_lock, config)
	else:
		files = [(filename, None)]

	# extract features and transmit
	for filename, speaker in files:
		features = feature_extraction.extract_features(filename)
		transmission.transmit(features, speaker)
		
		# if speaker diarization was used, new subfiles have been created and need to be removed
		if config.get("speaker_diarization"):
			os.remove(filename)


def analyze_audio_files(file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, setting_update):
	''' Analyzes files of audio extracting and processing speech

		Parameters:
			file_queue
				queue to get filenames from
			speaker_dictionary
				dictionary to store statistics about each speaker in
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently
			config
				CAT.settings.Config - all settings associated with the program
			threads_ready_to_update
				multiprocessing.Semaphore - indicates how many threads are currently ready for a settings update
			setting_update
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
	'''

	# analysis processes process files indefinitely
	while True:

		# block until a file is available in the queue
		filename = file_queue.get()
		
		# process the file
		analyze_audio_file(filename, speaker_dictionary, speaker_dictionary_lock, config)

		# delete the file
		os.remove(filename)

		transmission.check_for_updates(config, threads_ready_to_update, setting_update)

		# no files being processed
		# so this is a good time for a settings update
		threads_ready_to_update.release() # signal that this thread is ready to update settings
		setting_update.wait() # do not attempt to re-acquire the semaphore until the settings update is complete
		threads_ready_to_update.acquire() # signal that this thread is no longer ready to update settings


def start_processes():
	''' Starts all process of the program '''
	config = settings.Config()

	process_manager = Manager()
	speaker_dictionary = process_manager.dict()
	setting_update = Event()
	setting_update.set()
	threads_ready_to_update = Semaphore(0)
	speaker_dictionary_lock = Lock()
	file_queue = Queue() # thread-safe FIFO queue

	# ideally of the cores should run the record.recording process
	# and the other cores will run the analysis processes
	record.recording_process = Process(target=record.record, args=(file_queue, config, threads_ready_to_update, setting_update))
	record.recording_process.start()
	analysis_processes = [Process(target=analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, setting_update)) for _ in range(config.get("num_cores") - 1)]
	for process in analysis_processes:
		process.start()

	# block until the record.recording process exits (never, unless error)
	record.recording_process.join()


if __name__ == '__main__':
	start_processes()