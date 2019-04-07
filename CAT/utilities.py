import shutil
import os
import datetime
import wave


def get_output_directory():
	return os.path.join("CAT", "recordings")


def read_file(filename):
	''' Reads an audio file and returns a byte string of its contents

		Parameters:
			filename: str
		Returns:
			byte strings
	'''

	try:
		wave_file = wave.open(filename, 'rb')
		audio = wave_file.readframes(wave_file.getnframes())
		wave_file.close()
	except FileNotFoundError:
		audio = b''
		
	return audio


def save_to_file(data, config):
	''' Saves audio to a file

		Parameters:
			data
				the audio to save to the file
				type: byte string
			config
				CAT.settings.Config - all settings associated with the program
		Returns:
			the filename (str)
	'''

	total_bytes, used_bytes, free_bytes = shutil.disk_usage(get_output_directory())

	if free_bytes < config.get("min_empty_space_in_bytes"):
		raise IOError

	filename = os.path.join(get_output_directory(), "audio{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")))

	# save file with unique name indicating date and time
	wave_file = wave.open(filename, 'wb')
	wave_file.setnchannels(config.get("num_channels"))
	wave_file.setsampwidth(config.get("num_bytes"))
	wave_file.setframerate(config.get("rate"))
	wave_file.writeframes(data)
	wave_file.close()

	return filename