import datetime
import uuid
from numpy.linalg import norm
from CAT.settings import *


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


def add_new_speaker(audio_mean, audio_covariance, speaker_dictionary):
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
		Returns:
			new speaker ID generated
	'''

	# store a new speaker
	speaker_id = str(uuid.uuid4()) # generates a random ID, highly unlikely to be duplicated
	speaker_dictionary[speaker_id] = (audio_mean, audio_covariance, 1, datetime.datetime.now())

	return speaker_id


def identify_speaker(audio_mean, audio_covariance, speaker_dictionary, speaker_dictionary_lock):
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
		Returns:
			ID of the speaker in the audio
	'''

	speaker_dictionary_lock.acquire()

	# if there are no speakers yet, add a new one
	if len(speaker_dictionary) == 0:
		speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary)

	else:
		# find the previously recorded speaker with the lowest distance
		speaker_id = None
		speaker_mean = None
		speaker_covariance = None
		speaker_count = None
		distance = None
		for temp_speaker_id, (temp_speaker_mean, temp_speaker_covariance, temp_speaker_count, temp_speaker_last_seen) in speaker_dictionary.items():
			temp_distance = speaker_distance(temp_speaker_mean, temp_speaker_covariance, audio_mean, audio_covariance)
			if distance == None or (not temp_distance == None and temp_distance < distance):
				distance = temp_distance
				speaker_id = temp_speaker_id
				speaker_mean = temp_speaker_mean
				speaker_covariance = temp_speaker_covariance
				speaker_count = temp_speaker_count

		if distance == None: # distance is invalid on all pairs
			# add a new speaker
			speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary)
		elif distance <= SPEAKER_REID_DISTANCE_THRESHOLD:
			# update speaker values
			new_speaker_count = speaker_count + 1
			new_mean = (speaker_mean * speaker_count + audio_mean) / new_speaker_count
			new_covariance = (speaker_covariance * speaker_count + audio_covariance) / new_speaker_count
			speaker_dictionary[speaker_id] = (new_mean, new_covariance, new_speaker_count, datetime.datetime.now())
		else:
			# or add a new speaker
			speaker_id = add_new_speaker(audio_mean, audio_covariance, speaker_dictionary)

		# remove not recently seen speakers
		for speaker in list(speaker_dictionary.keys()):
			if datetime.datetime.now() - speaker_dictionary[speaker][3] > SPEAKER_FORGET_INTERVAL:
				speaker_dictionary.pop(speaker, None)

		# if there are too many speakers, remove rarely occuring ones
		while len(speaker_dictionary) > MAX_NUMBER_OF_SPEAKERS:
			deleted = speaker_dictionary.pop(
				min(speaker_dictionary, key=lambda key: speaker_dictionary.get(key)[2]),
				None
			)


	speaker_dictionary_lock.release()

	return speaker_id