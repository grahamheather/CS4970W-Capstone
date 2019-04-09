import requests
import uuid

def register_device(config, threads_ready_to_update, settings_update_event, settings_update_lock):
	''' Checks if this device has a valid ID.
		If not, it registers as a new device with the server.
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
			threads_ready_to_update
				multiprocessing.Semaphore - indicates how many threads are currently ready for a settings update
			settings_update_event
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
			settings_update_lock
				multiprocessing.Lock - allows only one process to update settings at a time (prevents semaphore acquisition deadlock)

	'''

	# Check if the device ID is valid
	if config.get("device_id") == 0:
		# generate new device ID
		handle = str(uuid.uuid4()) # generates a random ID

		# register the device with the server
		request_data = {"handle": handle}
		response = requests.post("{}/devices".format(config.get("server")), data=request_data)

		# get the new device's ID
		response_data = response.json()
		device_id = response_data["deviceId"]

		# update the settings with the new ID
		update_settings(
			config, 
			"device_id", device_id, 
			threads_ready_to_update, settings_update_event, settings_update_lock
		)


def update_device_settings(config):
	''' Update the settings associated with a device on the server
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
	'''

	request_data = {
		"id": config.get("device_id"),
		"settings": config.to_string()
	}
	requests.put("{}/devices/{}/settings".format(config.get("server"), config.get("device_id")), data=request_data)


def register_speaker(config, audio_mean, audio_covariance):
	''' Registers a new speaker with the server
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			str - new speaker ID
	'''

	# convert data into a transmittable format
	data = [audio_mean.tolist(), audio_covariance.tolist(), 1, datetime.datetime.now()]

	# register new speaker
	request_data = {
		"deviceId": config.get("device_id"),
		"data": data
	}
	response = requests.post("{}/speakers".format(config.get("server")), data=request_data)

	# get the new speakers's ID
	response_data = response.json()
	return response_data["speakerId"]


def get_speakers(config):
	''' Gets the ID and specifications of all speakers registered with this device
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			dict - {speaker ID: specifications}
	'''

	response = requests.get("{}/devices/{}/speakers".format(config.get("server"), config.get("device_id")))
	response_data = response.json()
	
	# convert dictionary format
	speaker_dictionary = {
		speaker["speakerId"]: [
			numpy.array(speaker["data"][0]), 
			numpy.array(speaker["data"][1]), 
			speaker["data"][2],
			speaker["data"][3]
		] 
		for speaker in response_data
	}

	return speaker_dictionary


def delete_speaker(config, speaker_id):
	''' 
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
			speaker_id
				str - ID of the speaker to delete
	'''

	request_data = {"id": speaker_id}
	requests.delete("{}/speakers/{}".format(config.get("server"), config.get("speaker_id")), data=request_data)


def update_speaker(config, speaker_id, speaker_mean, speaker_covariance, speaker_count):
	''' Registers a new speaker with the server
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			str - new speaker ID
	'''

	# convert data into a transmittable format
	data = [audio_mean.tolist(), audio_covariance.tolist(), speaker_count, datetime.datetime.now()]

	# register new speaker
	request_data = {
		"id": speaker_id,
		"data": data
	}
	requests.put("{}/speakers/{}".format(config.get("server"), speaker_id), data=request_data)


def transmit(features, speaker, config):
	''' Transmits features extracted from a slice of audio data
		Parameters:
			features
				the features extracted
			speaker
				str - the speaker detect in the audio data
			config
				CAT.settings.Config - all settings associated with the program
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