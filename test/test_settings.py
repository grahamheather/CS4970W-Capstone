import pytest
import unittest.mock as mock

# supporting libraries
import datetime
import os
import multiprocessing
import time
import wave
from multiprocessing.managers import BaseManager

from CAT import scheduling, record

# file under test
from CAT import settings

# testing file generation
import gen_audio


# this process can be slow
# it can be disabled if settings have not been changed (the necessary files are saved)
REGENERATE_FILES = False


# UTILITY FUNCTIONS
def get_package_dir():
	return 'CAT'


def get_test_recording_dir():
	return os.path.join('test', 'test_recordings')


# FIXTURES

@pytest.fixture(scope="session", autouse=True)
def generate_audio_files():
	if REGENERATE_FILES:
		gen_audio.generate_test_settings_audio(get_test_recording_dir())


@pytest.fixture()
def config():
	return settings.Config()


# fixture wrapping a wave file reader to the microphone input reader
@pytest.fixture()
def mock_stream(request, monkeypatch, config):
	class MockStream:
		i = 0 # track how many frames have been read

		def __init__(self, filename):
			self.wave_file = wave.open(filename, 'r')
			self.n = self.wave_file.getnframes()
			assert self.wave_file.getnchannels() == config.get("num_channels")
			assert self.wave_file.getsampwidth() == config.get("num_bytes")
			assert self.wave_file.getframerate() == config.get("rate")

		def read(self, frame_size):
			self.i = self.i + frame_size
			return self.wave_file.readframes(frame_size)
			

		def is_stopped(self):
			# note that this might cut off the end of the audio file
			return (self.i >= self.n - config.get("vad_frame_size") * config.get("periodic_sample_frames"))


	def mockreturn(settings):
		return MockStream(request.param)

	monkeypatch.setattr(record, "open_stream", mockreturn)


# remove temporary config file before each test
@pytest.fixture(autouse=True)
def cleanup():
	try:
		os.remove(os.path.join(get_package_dir(), "test_temp.ini"))
	except FileNotFoundError as e:
		print(e)


# TESTS

# test loading settings from file
def test_load_settings():
	result = settings.Config()

	# check that settings are loaded properly with the right types
	assert all([
		all(type(result.settings[name]) == int for name in
			["milliseconds_per_second", "num_cores", "min_empty_space_in_bytes",
				"vad_level", "num_bytes", "num_channels", "rate", "vad_frame_ms",
				"max_speakers", "speaker_reid_distance_threshold", "max_number_of_speakers"
			]				
		),
		all(type(result.settings[name]) == float for name in
			["periodic_sample_rate", "min_sample_length",
				"max_sample_length", "max_silence_length"
			]
		),
		all(type(result.settings[name]) == bool for name in
			["speaker_diarization"]
		),
		all(type(result.settings[name]) == datetime.timedelta for name in
			["speaker_forget_interval"]
		)
	])

	# check that calculated settings are also included
	assert all(name in result.settings for name in
		["vad_frame_size", "vad_frame_bytes", "format", "periodic_sample_rate",
			"min_sample_frames", "max_sample_frames", "max_silence_frames"
		]
	)


# test getting sentences
def test_get_settings():
	config = settings.Config()
	for setting in config.settings:
		assert config.get(setting) == config.settings[setting]


# test saving settings (integer)
def test_save_settings_integer(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "milliseconds_per_second"
	new_value = 500
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()

	# call function
	config.set(new_setting, new_value, semaphore, event)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that setting is updated in program
	assert config.get(new_setting) == new_value

	# test file created
	assert "test_temp.ini" in os.listdir(get_package_dir())

	# test that the setting appears in the file
	file = open(os.path.join(get_package_dir(), "test_temp.ini"), 'r')
	assert "{} = {}".format(new_setting, new_value) in file.read()

	# check that new setting reads properly
	config2 = settings.Config()
	assert config2.get(new_setting) == new_value


# test saving settings (float)
def test_save_settings_float(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "periodic_sample_rate"
	new_value = 1 / 9
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()

	# call function
	config.set(new_setting, new_value, semaphore, event)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that setting is updated in program
	assert config.get(new_setting) == new_value

	# test file created
	assert "test_temp.ini" in os.listdir(get_package_dir())

	# test that the setting appears in the file
	file = open(os.path.join(get_package_dir(), "test_temp.ini"), 'r')
	assert "{} = {}".format(new_setting, new_value) in file.read()

	# check that new setting reads properly
	config2 = settings.Config()
	assert config2.get(new_setting) == new_value


# test saving settings (boolean)
def test_save_settings_boolean(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "speaker_diarization"
	new_value = True
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()

	# call function
	config.set(new_setting, new_value, semaphore, event)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that setting is updated in program
	assert config.get("speaker_diarization") == True

	# test file created
	assert "test_temp.ini" in os.listdir(get_package_dir())

	# test that the setting appears in the file
	file = open(os.path.join(get_package_dir(), "test_temp.ini"), 'r')
	assert "speaker_diarization = True" in file.read()

	# check that new setting reads properly
	config2 = settings.Config()
	assert config2.get("speaker_diarization") == True


# test saving settings (datetime)
def test_save_settings_day(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "speaker_forget_interval"
	new_value = datetime.timedelta(days=500)
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()

	# call function
	config.set(new_setting, new_value, semaphore, event)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that setting is updated in program
	assert config.get(new_setting) == new_value

	# test file created
	assert "test_temp.ini" in os.listdir(get_package_dir())

	# test that the setting appears in the file
	file = open(os.path.join(get_package_dir(), "test_temp.ini"), 'r')
	assert "{} = 500".format(new_setting) in file.read()

	# check that new setting reads properly
	config2 = settings.Config()
	assert config2.get(new_setting) == new_value


# test not setting calculated fields
def test_save_settings_calculated(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "periodic_sample_frames"
	new_value = 0
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()

	# call function, test that an error is raised
	with pytest.raises(ValueError):
		config.set(new_setting, new_value, semaphore, event)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that setting is not updated in program
	assert not config.get(new_setting) == new_value

	# test file not created
	assert not "test_temp.ini" in os.listdir(get_package_dir())


# test that settings are not set if the semaphore is not available
def test_save_settings_no_semaphore_boolean(monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "speaker_diarization"
	new_value = True
	semaphore = multiprocessing.Semaphore(config.get("num_cores") - 2) # the process will release one semaphore itself
	event = multiprocessing.Event()
	event.set()

	# call function
	process = multiprocessing.Process(target=config.set, args=(new_setting, new_value, semaphore, event))
	process.start()

	# give the Process time to finish the updatep
	time.sleep(1)

	# stop the Process (it should be stuck, waiting)
	process.terminate()

	# test that setting is not updated in program
	assert not config.get("speaker_diarization") == True

	# test file is not created
	assert not "test_temp.ini" in os.listdir(get_package_dir())


# test managing processes and pause recording while updating settings
@pytest.mark.parametrize('mock_stream', [os.path.join(get_test_recording_dir(), 'settings_twice.wav')], indirect=['mock_stream'])
#@mock.patch("CAT.scheduling.analyze_audio_file")
#@mock.patch("CAT.scheduling.os.remove")
#@mock.patch("CAT.scheduling.transmission.check_for_updates")
def test_save_settings_manage_processes(mock_stream, monkeypatch): #transmission_update_mock, remove_mock, analyze_mock, mock_stream, monkeypatch):
	analyze_mock = mock.Mock()
	monkeypatch.setattr(scheduling, "analyze_audio_file", analyze_mock)

	#analyze_mock("random")

	# initialize config
	BaseManager.register('Config', settings.Config)
	config_manager = BaseManager()
	config_manager.start()
	config = config_manager.Config()


	semaphore = multiprocessing.Semaphore(config.get("num_cores") - 1)
	event = multiprocessing.Event()
	event.set()
	# add a new test variable
	#multiprocessing.Process(target=config.set, args=("test_setting", 123))
	config.set(
		"test_setting", 
		12345, 
		semaphore,
		event
	)

	# multiprocess shared parameters
	process_manager = multiprocessing.Manager()
	speaker_dictionary = process_manager.dict()
	setting_update = multiprocessing.Event()
	setting_update.set()
	threads_ready_to_update = multiprocessing.Semaphore(config.get("num_cores") - 3)
	speaker_dictionary_lock = multiprocessing.Lock()
	file_queue = multiprocessing.Queue() # thread-safe FIFO queue

	# start updating a setting
	process = multiprocessing.Process(target=config.set, args=("test_setting", 9876, threads_ready_to_update, setting_update))
	process.start()

	# start the process (just one of each)
	recording_process = multiprocessing.Process(target=record.record, args=(file_queue, config, threads_ready_to_update, setting_update))
	recording_process.start()
	analysis_process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, setting_update))
	analysis_process.start()

	# give the Processes time to run
	time.sleep(1)

	recording_process.terminate()
	analysis_process.terminate()

	#print(analyze_mock.mock_calls)
	#print(transmission_update_mock.mock_calls)
	#print(remove_mock.mock_calls)
	print(config.get("test_setting"))
	assert False
