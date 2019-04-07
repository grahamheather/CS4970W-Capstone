# multiprocessing avoids Python's Global Interpreter Lock which
# prevents more than one thread running at a time.
# This allows the program to, ideally, take advantage of multiple
# cores on the Raspberry Pi.
from multiprocessing import Process, Queue, Manager, Value, Lock, Event, Semaphore
from multiprocessing.managers import BaseManager

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


def analyze_audio_files(file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, settings_update_event, settings_update_lock):
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
			settings_update_event
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
			settings_update_lock
				multiprocessing.Lock - allows only one process to update settings at a time (prevents semaphore acquisition deadlock)

	'''

	# analysis processes process files indefinitely
	while True:

		# block until a file is available in the queue
		filename = file_queue.get()
		
		# process the file
		analyze_audio_file(filename, speaker_dictionary, speaker_dictionary_lock, config)

		# delete the file
		os.remove(filename)

		transmission.check_for_updates(config, threads_ready_to_update, settings_update_event)

		# no files being processed
		# so this is a good time for a settings update
		threads_ready_to_update.release() # signal that this thread is ready to update settings
		settings_update_event.wait() # do not attempt to re-acquire the semaphore until the settings update is complete
		threads_ready_to_update.acquire() # signal that this thread is no longer ready to update settings


def start_processes():
	''' Starts all process of the program '''

	# initialize a multiprocessing Config object
	BaseManager.register('Config', settings.Config)
	config_manager = BaseManager()
	config_manager.start()
	config = config_manager.Config()

	process_manager = Manager()
	speaker_dictionary = process_manager.dict()
	settings_update_event = Event()
	settings_update_event.set()
	threads_ready_to_update = Semaphore(0)
	settings_update_lock = Lock()
	speaker_dictionary_lock = Lock()
	file_queue = Queue() # thread-safe FIFO queue

	# ideally of the cores should run the record.recording process
	# and the other cores will run the analysis processes
	recording_process = Process(target=record.record, args=(file_queue, config, threads_ready_to_update, settings_update_event))
	recording_process.start()
	analysis_processes = [Process(target=analyze_audio_files, args=(
			file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, settings_update_event, settings_update_lock)
		) for _ in range(config.get("num_cores") - 1)]
	for process in analysis_processes:
		process.start()

	# block until the record.recording process exits (never, unless error)
	recording_process.join()


if __name__ == '__main__':
	start_processes()