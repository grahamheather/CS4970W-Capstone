import pytest

# supporting libraries
import multiprocessing
import os
import numpy
import requests
import datetime
import json
import datetime

from CAT import settings

# file under test
from CAT import transmission


# UTILITY FUNCTIONS
def get_package_dir():
	return 'CAT'


# FIXTURES

# remove temporary config file before each test
@pytest.fixture(autouse=True)
def cleanup():
	try:
		os.remove(os.path.join(get_package_dir(), "test_temp.ini"))
	except FileNotFoundError as e:
		print(e)


# TESTS

def test_register_device_already_registered(monkeypatch):
	# set up config with a registed device ID
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")
	config.set("device_id", "SOME_ID")

	# call device registration
	transmission.register_device(config)

	# check that the device id has not changed
	assert config.get("device_id") == "SOME_ID"


def test_register_device(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# call device registration
	transmission.register_device(config)

	# check that the device id was updated
	assert not config.get("device_id") == "None"
	assert not config.get("settings_id") == "None"

	# clean up server
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_update_device_settings(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")
	
	# register a device with the server
	transmission.register_device(config)

	# get old settings ID
	old_settings_id = config.get("settings_id")

	# update a setting
	config.set("min_empty_space_in_bytes", 3)

	# call update settings on server
	settings_id = transmission.update_device_settings(config)

	# check that the settings ID is updated
	assert not settings_id == old_settings_id

	# check that the settings are up to date on the server
	response = requests.get("{}/devices/settings/{}".format(config.get("server"), settings_id))
	response_data = response.json()
	assert json.loads(response_data["properties"])["min_empty_space_in_bytes"] == 3

	# clean up server
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_register_speaker(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")
	
	# register a device with the server
	transmission.register_device(config)

	# testing data
	audio_mean = numpy.array([1, 2])
	audio_covariance = numpy.array([[1, 2], [3, 4]])

	# call speaker registration
	result = transmission.register_speaker(config, audio_mean, audio_covariance)

	# check that valid speaker ID is returned
	assert type(result) == str

	# clean up server
	requests.delete("{}/speakers/{}".format(config.get("server"), result))
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_get_speakers(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# register a device with the server
	transmission.register_device(config)

	# testing data
	means = [numpy.array([1, 2]), numpy.array([2, 3]), numpy.array([3, 4])]
	covariances = [numpy.array([[1, 2], [3, 4]]), numpy.array([[0, 0], [0, 0]]), numpy.array([[2, 3], [4, 5]])]
	
	# register speakers
	ids = []
	for mean, covariance in zip(means, covariances):
		ids.append(transmission.register_speaker(config, mean, covariance))

	# call get speakers
	result = transmission.get_speakers(config)

	# check that proper result was returned
	assert set(result.keys()) == set(ids)
	for i in range(len(ids)):
		assert (result[ids[i]][0] == means[i]).all()
		assert (result[ids[i]][1] == covariances[i]).all()
		assert result[ids[i]][2] == 1
		assert type(result[ids[i]][3]) == datetime.datetime

	# clean up server
	for speaker_id in ids:
		requests.delete("{}/speakers/{}".format(config.get("server"), speaker_id))
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_delete_speaker(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# register a device with the server
	transmission.register_device(config)

	# testing data
	mean = numpy.array([1, 2])
	covariance = numpy.array([[1, 2], [3, 4]])

	# register speaker
	speaker_id = transmission.register_speaker(config, mean, covariance)
	
	# check that speaker was registered
	response = requests.get("{}/speakers/{}".format(config.get("server"), speaker_id))
	assert response.status_code == 200	

	# call delete speaker
	transmission.delete_speaker(config, speaker_id)

	# check that speaker no longer exists
	response = requests.get("{}/speakers/{}".format(config.get("server"), speaker_id))
	assert response.status_code == 404

	# clean up server
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_update_speaker(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# register a device with the server
	transmission.register_device(config)

	# testing data
	mean = numpy.array([1, 2])
	covariance = numpy.array([[1, 2], [3, 4]])

	# register speaker
	speaker_id = transmission.register_speaker(config, mean, covariance)
	
	# check that speaker was registered
	response = requests.get("{}/speakers/{}".format(config.get("server"), speaker_id))
	assert response.status_code == 200	

	# update data
	new_mean = numpy.array([5, 6])
	new_covariance = numpy.array([[0, 1], [1, 0]])
	new_count = 5

	# call update speaker
	transmission.update_speaker(config, speaker_id, new_mean, new_covariance, new_count)

	# check that the speaker was updated
	speakers = transmission.get_speakers(config)
	assert speaker_id in speakers
	print(speakers[speaker_id])
	assert (speakers[speaker_id][0] == new_mean).all()
	assert (speakers[speaker_id][1] == new_covariance).all()
	assert speakers[speaker_id][2] == new_count
	assert type(speakers[speaker_id][3]) == datetime.datetime

	# clean up server
	requests.delete("{}/speakers/{}".format(config.get("server"), speaker_id))
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_transmit_speaker(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# register a device with the server
	transmission.register_device(config)

	# testing speaker data
	mean = numpy.array([1, 2])
	covariance = numpy.array([[1, 2], [3, 4]])

	# register speaker
	speaker_id = transmission.register_speaker(config, mean, covariance)

	# transmit data
	transmission.transmit({"some_feature1": 0, "some_feature2": 1}, speaker_id, config)

	# check that the data is on the server
	response = requests.get("{}/devices/{}/recordings".format(config.get("server"), config.get("device_id")))	
	response_data = response.json()
	recording = requests.get("{}/recordings/{}".format(config.get("server"), response_data[0]["recordingId"]))
	recording_data = recording.json()
	assert len(response_data) == 1
	assert json.loads(recording_data["data"]) == {"some_feature1": 0, "some_feature2": 1}
	assert response_data[0]["speakerId"] == speaker_id

	# clean up server
	requests.delete("{}/speakers/{}".format(config.get("server"), speaker_id))
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_transmit_no_speaker(monkeypatch):
	# set up config
	config = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# register a device with the server
	transmission.register_device(config)

	# transmit data
	transmission.transmit({"some_feature1": 0, "some_feature2": 1}, None, config)

	# check that the data is on the server
	response = requests.get("{}/devices/{}/recordings".format(config.get("server"), config.get("device_id")))	
	response_data = response.json()
	recording = requests.get("{}/recordings/{}".format(config.get("server"), response_data[0]["recordingId"]))
	recording_data = recording.json()
	assert len(response_data) == 1
	assert json.loads(recording_data["data"]) == {"some_feature1": 0, "some_feature2": 1}
	assert response_data[0]["speakerId"] == None

	# clean up server
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))


def test_check_for_updates(monkeypatch):
	# set up config
	config = settings.Config()
	config2 = settings.Config()
	monkeypatch.setattr(settings, "FILENAME", "test_temp.ini")

	# multiprocessing objects
	semaphore = multiprocessing.Semaphore(config.get("num_cores"))
	event = multiprocessing.Event()
	event.set()
	lock = multiprocessing.Lock()

	# register a device with the server
	transmission.register_device(config)

	# keep old settings id
	old_settings_id = config.get("settings_id")

	# simulate changing a setting on the server
	config2.set("min_empty_space_in_bytes", 25)
	config2.set("speaker_forget_interval", 21)
	requests.put("{}/devices/{}/settings".format(config.get("server"), config.get("device_id")),
		data={"settings": config2.to_string()}
	)

	# call check for updates
	transmission.check_for_updates(config, semaphore, event, lock)

	# check that settings were updated
	assert config.get("min_empty_space_in_bytes") == 25
	assert config.get("speaker_forget_interval") == datetime.timedelta(days=21)
	assert not config.get("settings_id") == old_settings_id

	# clean up server
	requests.delete("{}/devices/{}".format(config.get("server"), config.get("device_id")))