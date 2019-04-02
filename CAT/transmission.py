def transmit(features, speaker):
	''' Transmits features extracted from a slice of audio data
		Parameters:
			features
				the features extracted
			speaker
				the speaker detect in the audio data
	'''

	return


def check_for_updates(config, threads_ready_to_update, setting_update):
	''' Updates settings if they need to be updated
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
			threads_ready_to_update
				multiprocessing.Semaphore - indicates how many threads are currently ready for a settings update
			setting_update
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
	'''

	# calls config.set() if an update is necessary
	# updates cause significant slow-downs, do not call config.set() if an update is not necessary

	return