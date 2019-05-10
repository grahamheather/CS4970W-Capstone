import datetime
from numpy.linalg import norm

from CAT import transmission


def speaker_distance(mean0, covariance0, mean1, covariance1):
	''' Calculates the distance between two speakers

		Parameters:
			mean0
				mean of PDF 0
			covariance0
				covariance matrix of PDF 0
			mean1
				mean of PDF 1
			covariance1
				covariance matrix of PDF 1

		Returns:
			float, the distance
	'''

	# Note that current implementation does not use covariances
	# Covariances are retained for ease of modification in the future

	# Using Euclidean distance between means
	return norm(mean0 - mean1)


def add_new_speaker(audio_mean, audio_covariance, speaker_dictionary, config):
	''' Utility function to add a new speaker to the dictionary

		Parameters:
			audio_mean
				mean of the multivariate normal PDF of the new speaker
			audio_covariance
				covariance matrix of the multivariate normal PDF of the new speaker
			speaker_dictionary
				dictionary of previously recorded speakers
				{
					'speakerID': (mean, covariance, count, last seen)
				}
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			new speaker ID generated
	'''

	# store a new speaker
	speaker_id = transmission.register_speaker(config, audio_mean, audio_covariance)
	speaker_dictionary[speaker_id] = {
		"mean": audio_mean, 
		"covariance": audio_covariance, 
		"count": 1, 
		"last_seen": datetime.datetime.now()
	}

	return speaker_id


def identify_speaker(audio_mean, audio_covariance, speaker_dictionary, speaker_dictionary_lock, config):
	''' Matches a speaker in an audio file to a previously recorded
		speaker

		Parameters:
			audio_mean
				mean of the multivariate normal PDF of the new speaker
			audio_covariance
				covariance matrix of the multivariate normal PDF of the new speaker
			speaker_dictionary
				dictionary of previously recorded speakers
				{
					'speakerID': (mean, covariance, count, last seen)
				}
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			ID of the speaker in the audio
	'''

	speaker_dictionary_lock.acquire()

	# if there are no speakers yet, add a new one
	if len(speaker_dictionary) == 0:
		speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary, config)

	else:
		# find the previously recorded speaker with the lowest distance
		speaker_id = None
		speaker_mean = None
		speaker_covariance = None
		speaker_count = None
		distance = None
		for temp_speaker_id, speaker_data in speaker_dictionary.items():
			temp_distance = speaker_distance(speaker_data["mean"], speaker_data["covariance"], audio_mean, audio_covariance)
			if distance == None or (not temp_distance == None and temp_distance < distance):
				distance = temp_distance
				speaker_id = temp_speaker_id
				speaker_mean = speaker_data["mean"]
				speaker_covariance = speaker_data["covariance"]
				speaker_count = speaker_data["count"]

		if distance == None: # distance is invalid on all pairs
			# add a new speaker
			speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary, config)
		elif distance <= config.get("speaker_reid_distance_threshold"):
			# update speaker values
			new_speaker_count = speaker_count + 1
			new_mean = (speaker_mean * speaker_count + audio_mean) / new_speaker_count
			new_covariance = (speaker_covariance * speaker_count + audio_covariance) / new_speaker_count
			speaker_dictionary[speaker_id] = {
				"mean": new_mean, 
				"covariance": new_covariance, 
				"count": new_speaker_count, 
				"last_seen": datetime.datetime.now()
			}
			transmission.update_speaker(config, speaker_id, new_mean, new_covariance, new_speaker_count)
		else:
			# or add a new speaker
			speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary, config)

		# remove not recently seen speakers
		for speaker_to_delete in list(speaker_dictionary.keys()):
			if datetime.datetime.now() - speaker_dictionary[speaker_to_delete]["last_seen"] > config.get("speaker_forget_interval"):
				transmission.delete_speaker(config, speaker_to_delete)
				speaker_dictionary.pop(speaker_to_delete, None)

		# if there are too many speakers, remove rarely occuring ones
		while len(speaker_dictionary) > config.get("max_number_of_speakers"):
			speaker_to_delete = min(speaker_dictionary, key=lambda key: speaker_dictionary.get(key)["count"])
			transmission.delete_speaker(config, speaker_to_delete)
			deleted = speaker_dictionary.pop(
				speaker_to_delete,
				None
			)


	speaker_dictionary_lock.release()

	return speaker_id