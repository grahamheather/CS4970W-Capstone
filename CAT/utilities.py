import os
import datetime
import wave
from CAT.settings import *


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


def save_to_file(data):
	''' Saves audio to a file

		Parameters:
			data
				the audio to save to the file
				type: byte string
		Returns:
			the filename (str)
	'''

	filename = os.path.join(get_output_directory(), "audio{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")))

	# save file with unique name indicating date and time
	wave_file = wave.open(filename, 'wb')
	wave_file.setnchannels(NUM_CHANNELS)
	wave_file.setsampwidth(NUM_BYTES)
	wave_file.setframerate(RATE)
	wave_file.writeframes(data)
	wave_file.close()

	return filename