import pyaudio
import datetime
import configparser
from multiprocessing import Lock
from os import path

from CAT import transmission

FILENAME = "config.ini"


class Config():
	''' A class to contain all of the data and functions associated with
		getting, updating, and writing settings to disk.
	'''

	def __init__(self):
		''' Read settings from the config.ini file '''
		
		self.settings = {}

		# read settings file
		self.config = configparser.ConfigParser()
		self.config.read(path.join("CAT", FILENAME))

		# read by value type
		for key in self.config["Integer Values"]:
			self.settings[key] = self.config["Integer Values"].getint(key)
		for key in self.config["Float Values"]:
			self.settings[key] = self.config["Float Values"].getfloat(key)
		for key in self.config["Boolean Values"]:
			self.settings[key] = self.config["Boolean Values"].getboolean(key)
		for key in self.config["Day Values"]:
			self.settings[key] = datetime.timedelta(days=int(self.config["Day Values"][key]))
		for key in self.config["String Values"]:
			self.settings[key] = self.config["String Values"][key]

		# calculated values
		self.calculated_fields = set(["vad_frame_size", "vad_frame_bytes", "format", "periodic_sample_frames", "min_sample_frames", "max_sample_frames", "max_silence_frames"])
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
		if name in self.calculated_fields:
			raise ValueError("Calculated fields cannot be manually set")


		# update in active data structure
		self.settings[name] = value

		# update in config
		found = False
		for section in self.config:
			for key in self.config[section]:
				if key == name:
					if type(value) == datetime.timedelta:
						self.config.set(section, key, str(value.days))
					else:
						self.config.set(section, key, str(value))
					found = True
					break
			if found == True:
				break

		# update the config file on disk
		with open(path.join("CAT", FILENAME), 'w') as self.config_file:
			self.config.write(self.config_file)


	def to_string(self):
		''' Return a string version of the settings for transmission
			Returns:
				str
		'''

		return str(self.settings)



def update_settings(config, name, value, threads_ready_to_update, settings_update_event, settings_update_lock):
	''' Coordinate multiple processes while updating settings

		Parameters:
			config - CAT.settings.Config, the config file to update the setting in
			name - str, the name of the setting (all lowercase, case sensitive)
			value - the new value of the setting
			threads_ready_to_update
				multiprocessing.Semaphore - indicates how many threads are currently ready for a settings update
			setting_update
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
			settings_update_lock
				multiprocessing.Lock - allows only one process to update settings at a time (prevents semaphore acquisition deadlock)

	'''

	# have the thread release its own semaphore before updating to prevent deadlock
	threads_ready_to_update.release()

	# acquire lock to edit
	settings_update_lock.acquire()

	# notify other processes that a settings update is occurring
	settings_update_event.clear()

	# wait until all other processes are ready to update
	for _ in range(config.get("num_cores")):
		threads_ready_to_update.acquire()

	# update setting
	config.set(name, value)

	# notify server of update
	transmission.update_device_settings(config)

	# release the other processes to continue
	for _ in range(config.get("num_cores")):
		threads_ready_to_update.release()

	# notify other processes that the settings update is over
	settings_update_event.set()

	# release lock
	settings_update_lock.release()

	# have the thread regain its own semaphore
	threads_ready_to_update.acquire()