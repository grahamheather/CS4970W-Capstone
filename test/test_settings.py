import pytest
import unittest.mock as mock

# supporting libraries
import datetime
import os
import multiprocessing
import time
import wave
from multiprocessing.managers import BaseManager
from shutil import copyfile

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
				"max_speakers", "speaker_reid_distance_threshold", "max_number_of_speakers",
				"device_id"
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
		),
		all(type(result.settings[name]) == str for name in
			["server"]
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


# test converting the settings to a string
def test_settings_to_string():
	config = settings.Config()
	assert type(config.to_string()) == str


# test saving settings (integer)
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_integer(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function
	settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that the lock was released
	lock.acquire()

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

	# test that the server was notified
	transmission_mock.assert_called_once_with(config)


# test saving settings (float)
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_float(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function
	settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that the lock was released
	lock.acquire()

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

	# test that the server was notified
	transmission_mock.assert_called_once_with(config)


# test saving settings (boolean)
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_boolean(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function
	settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that the lock was released
	lock.acquire()

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

	# test that the server was notified
	transmission_mock.assert_called_once_with(config)


# test saving settings (datetime)
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_day(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function
	settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that the lock was released
	lock.acquire()

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

	# test that the server was notified
	transmission_mock.assert_called_once_with(config)


# test saving settings (string)
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_string(transmission_mock, monkeypatch):
	# initialize config
	config = settings.Config()

	# mock filename so it saves in a different file to examine
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# parameters
	new_setting = "server"
	new_value = "https://en.wikipedia.org"
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()
	lock = multiprocessing.Lock()

	# call function
	settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that the event is reset
	assert event.is_set()

	# test that all semaphores were released
	for _ in range(config.get("num_cores")):
		semaphore.acquire()

	# test that the lock was released
	lock.acquire()

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

	# test that the server was notified
	transmission_mock.assert_called_once_with(config)


# test not setting calculated fields
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_calculated(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function, test that an error is raised
	with pytest.raises(ValueError):
		settings.update_settings(config, new_setting, new_value, semaphore, event, lock)

	# test that setting is not updated in program
	assert not config.get(new_setting) == new_value

	# test file not created
	assert not "test_temp.ini" in os.listdir(get_package_dir())

	# test that the server was not notified
	transmission_mock.assert_not_called()


# test that settings are not set if the semaphore is not available
@mock.patch("CAT.settings.transmission.update_device_settings")
def test_save_settings_no_semaphore_boolean(transmission_mock, monkeypatch):
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
	lock = multiprocessing.Lock()

	# call function
	process = multiprocessing.Process(target=settings.update_settings, args=(config, new_setting, new_value, semaphore, event, lock))
	process.start()

	# give the Process time to finish the updatep
	time.sleep(1)

	# stop the Process (it should be stuck, waiting)
	process.terminate()

	# test that setting is not updated in program
	assert not config.get("speaker_diarization") == True

	# test file is not created
	assert not "test_temp.ini" in os.listdir(get_package_dir())

	# test that the server was not notified
	transmission_mock.assert_not_called()


# test managing processes and pause recording while updating settings
@pytest.mark.parametrize('mock_stream', [os.path.join(get_test_recording_dir(), 'settings_twice.wav')], indirect=['mock_stream'])
def test_save_settings_manage_processes(mock_stream, monkeypatch):
	# make new config file that can be edited
	testing_config_file = os.path.join(get_test_recording_dir(), "test_temp.ini")
	copyfile(os.path.join(get_package_dir(), settings.FILENAME), testing_config_file)
	monkeypatch.setattr(settings, "FILENAME", os.path.join("..", testing_config_file))

	# set mocks
	analysis_calls = multiprocessing.Queue()
	def analyze_mock(file_queue, speaker_dictionary, speaker_dictionary_lock, configs):
		analysis_calls.put(config.get("device_id"))
	monkeypatch.setattr(scheduling, "analyze_audio_file", analyze_mock)

	transmission_check_calls = multiprocessing.Queue()
	def transmission_check_mock(config, threads_ready_to_update, settings_update_event):
		transmission_check_calls.put(config.get("device_id"))
	monkeypatch.setattr(scheduling.transmission, "check_for_updates", transmission_check_mock)

	transmission_update_calls = multiprocessing.Queue()
	def transmission_update_mock(config):
		transmission_update_calls.put(config.get("device_id"))
	monkeypatch.setattr(scheduling.transmission, "update_device_settings", transmission_update_mock)

	queue_calls = multiprocessing.Queue()
	original_function = record.queue_audio_buffer
	def queue_mock(audio_buffer, file_queue, config):
		queue_calls.put(config.get("device_id"))
		original_function(audio_buffer, file_queue, config)
	with mock.patch("CAT.record.queue_audio_buffer", wraps=queue_mock):

		# initialize config
		BaseManager.register('Config', settings.Config)
		config_manager = BaseManager()
		config_manager.start()
		config = config_manager.Config()
		
		# multiprocess shared parameters
		process_manager = multiprocessing.Manager()
		speaker_dictionary = process_manager.dict()
		settings_update_event = multiprocessing.Event()
		settings_update_event.set()
		threads_ready_to_update = multiprocessing.Semaphore(config.get("num_cores") - 1)
		settings_update_lock = multiprocessing.Lock()
		speaker_dictionary_lock = multiprocessing.Lock()
		file_queue = multiprocessing.Queue() # thread-safe FIFO queue

		# start the process (just one of each)
		recording_process = multiprocessing.Process(target=record.record, args=(file_queue, config, threads_ready_to_update, settings_update_event))
		recording_process.start()
		analysis_process = multiprocessing.Process(target=scheduling.analyze_audio_files, args=(file_queue, speaker_dictionary, speaker_dictionary_lock, config, threads_ready_to_update, settings_update_event, settings_update_lock))
		analysis_process.start()

		# start updating a setting
		process = multiprocessing.Process(target=settings.update_settings, args=(config, "device_id", 9876, threads_ready_to_update, settings_update_event, settings_update_lock))
		process.start()

		# give the Processes time to run
		time.sleep(2)

		# terminate all processes
		process.terminate()
		recording_process.terminate()
		analysis_process.terminate()

		# check that the setting was updated
		assert config.get("device_id") == 9876

		# clean up
		config_manager.shutdown()

		# check that setting was updated when expected
		assert analysis_calls.qsize() == 2
		assert analysis_calls.get() == 0
		assert analysis_calls.get() == 9876

		assert transmission_check_calls.qsize() == 2
		assert transmission_check_calls.get() == 0
		assert transmission_check_calls.get() == 9876

		assert queue_calls.qsize() == 2
		assert queue_calls.get() == 0
		assert queue_calls.get() == 9876

		assert transmission_update_calls.qsize() == 1
		assert transmission_update_calls.get() == 9876
		

		# test that the setting appears in the file
		file = open(testing_config_file, 'r')
		assert "device_id = 9876" in file.read()

		# check that new setting reads properly
		config2 = settings.Config()
		assert config2.get("device_id") == 9876

		# clean up
		os.remove(testing_config_file)