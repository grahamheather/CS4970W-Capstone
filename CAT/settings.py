import pyaudio
import datetime
import configparser
from multiprocessing import Lock
from os import path


class Config():
	''' A class to contain all of the data and functions associated with
		getting, updating, and writing settings to disk.
	'''

	def __init__(self):
		''' Read settings from the config.ini file '''
		
		self.settings = {}

		# read settings file
		self.config = configparser.ConfigParser()
		self.config.read(path.join("CAT", "config.ini"))

		# read by value type
		for key in self.config["Integer Values"]:
			self.settings[key] = self.config["Integer Values"].getint(key)
		for key in self.config["Float Values"]:
			self.settings[key] = self.config["Float Values"].getfloat(key)
		for key in self.config["Boolean Values"]:
			self.settings[key] = self.config["Boolean Values"].getboolean(key)
		for key in self.config["Day Values"]:
			self.settings[key] = datetime.timedelta(days=int(self.config["Day Values"][key]))

		# calculated values
		calculated_fields = set(["vad_frame_size", "vad_frame_bytes", "format", "periodic_sample_frames", "min_sample_frames", "max_sample_frames", "max_silence_frames"])
		# audio recording self.settings
		self.settings["vad_frame_size"] = int(
			self.settings["rate"] * self.settings["vad_frame_ms"] / self.settings["milliseconds_per_second"]
		)
		self.settings["vad_frame_bytes"] = self.settings["vad_frame_size"] * self.settings["num_bytes"] * self.settings["num_channels"]
		self.settings["format"] = pyaudio.paInt16 # WebRTC VAD only accepts 16-bit audio
		
		# calculated from system self.settings
		self.settings["periodic_sample_frames"] = int(
			self.settings["periodic_sample_rate"] * self.settings["milliseconds_per_second"] / self.settings["vad_frame_ms"]
		)
		self.settings["min_sample_frames"] = int(
			self.settings["min_sample_length"] * self.settings["milliseconds_per_second"] / self.settings["vad_frame_ms"]
		)
		self.settings["max_sample_frames"] = int(
			self.settings["max_sample_length"] * self.settings["milliseconds_per_second"] / self.settings["vad_frame_ms"]
		)
		self.settings["max_silence_frames"] = int(
			self.settings["max_silence_length"] * self.settings["milliseconds_per_second"] / self.settings["vad_frame_ms"]
		)

		self.settings_lock = Lock()


	def get(self, name):
		''' Get the value of a setting

			Parameters:
				name - str, the name of the setting (all lowercase, case sensitive)

			Returns:
				the value of the setting

		'''
		return self.settings[name]


	def set(self, name, value):
		''' Set the value of a setting

			Parameters:
				name - str, the name of the setting (all lowercase, case sensitive)
				value - the new value of the setting

		'''

		# check input
		if name in calculated_fields:
			raise 

		# acquire lock to edit
		self.settings_lock.acquire()

		# update in active data structure
		self.settings[name] = value

		# update in self.config
		found = False
		for section in self.config:
			for key in section:
				if key == name:
					self.config[section][key] == str(value)
					found = True
					break
			if found == True:
				break

		with open(path.join("CAT", "config.ini"), 'w') as self.config_file:
			self.config.write(self.config_file)

		self.settings_lock.release()