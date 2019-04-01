import pytest
import unittest.mock as mock


# supporting libraries
import pickle
import pyaudio
import wave
from os import path
import os
from queue import Queue

from CAT import settings

# file under test
from CAT import record

# testing file generation
import gen_audio


# this process can be slow
# it can be disabled if settings have not been changed (the necessary files are saved)
REGENERATE_FILES = False


# UTILITY FUNCTIONS
def get_recording_dir():
	return path.join('CAT', 'recordings')


def get_test_recording_dir():
	return path.join('test', 'test_recordings')


def read_wav(filename):
	wave_file = wave.open(filename, 'r')
	return wave_file.readframes(wave_file.getnframes())


# FIXTURES

@pytest.fixture(scope="session", autouse=True)
def generate_audio_files():
	if REGENERATE_FILES:
		stats = gen_audio.generate_test_record_audio(get_test_recording_dir())
		with open(path.join(get_test_recording_dir(), 'test_record_stats.pickle'), 'wb') as f:
			pickle.dump(stats, f)
	else:
		with open(path.join(get_test_recording_dir(), 'test_record_stats.pickle'), 'rb') as f:
			stats = pickle.load(f)

	return stats


@pytest.fixture(scope="session", autouse=True)
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


# remove all recordings from previous tests before each new test
@pytest.fixture(autouse=True)
def cleanup():
	for filename in os.listdir(get_recording_dir()):
		file_path = path.join(path.join(get_recording_dir(), filename))
		try:
			os.remove(file_path)
		except Exception as e:
			print(e)


# TESTS

# test opening stream
def test_open_stream(config):
	result = record.open_stream(config)
	assert type(result) == pyaudio.Stream


# test saving to file
def test_queue_audio_buffer(config):
	wave_file = wave.open(path.join(get_test_recording_dir(), 'hello.wav'), 'r')
	audio_buffer = [
		wave_file.readframes(config.get("vad_frame_size")) for i in range(
			int(wave_file.getnframes() / config.get("vad_frame_size") + .5 ) ) ]
	file_queue = Queue()
	record.queue_audio_buffer(audio_buffer, file_queue, config)

	assert file_queue.qsize() == 1
	filename = file_queue.get()
	assert len(os.listdir(get_recording_dir())) == 1
	assert os.path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]) == filename

	saved_file = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	wave_file.rewind()
	assert saved_file == wave_file.readframes(wave_file.getnframes())


# test attempting to save a file whe out of disk space
@mock.patch('CAT.record.utilities.save_to_file')
def test_queue_audio_buffer_error(save_mock, config):
	# set up mock
	save_mock.side_effect = IOError()

	# attempt to queue the audio buffer
	wave_file = wave.open(path.join(get_test_recording_dir(), 'hello.wav'), 'r')
	audio_buffer = [
		wave_file.readframes(config.get("vad_frame_size")) for i in range(
			int(wave_file.getnframes() / config.get("vad_frame_size") + .5) ) ]
	file_queue = Queue()
	record.queue_audio_buffer(audio_buffer, file_queue, config)

	# check that the buffer was not queued
	assert file_queue.qsize() == 0


# test that feeding only silence will not save a file
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'silence.wav')], indirect=['mock_stream'])
def test_silence(mock_stream, config):
	record.record(Queue(), config)
	assert os.listdir(get_recording_dir()) == []


# test that speech less than the min sample length will not save a file
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello.wav')], indirect=['mock_stream'])
def test_short(mock_stream, config):
	record.record(Queue(), config)
	assert os.listdir(get_recording_dir()) == []


# test that speech less than min sample length will not save a file but future speech will save a file
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+how.wav')], indirect=['mock_stream'])
def test_short_long(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+how.wav'))
	start, end = generate_audio_files['hello+how']
	desired_speech = original[start + 5000:end - 5000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < 0.5


# test that speech between the min and max sample lengths saves a single file
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'ground.wav')], indirect=['mock_stream'])
def test_normal(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'ground.wav'))
	start, end = generate_audio_files["ground"]
	desired_speech = original[start + 10000:end - 40000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < 0.5


# test that speech longer than the max sample length will save multiple files
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'tale.wav')], indirect=['mock_stream'])
def test_too_long(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	files = sorted(os.listdir(get_recording_dir()))
	assert len(files) == 2
	recording1 = read_wav(path.join(get_recording_dir(), files[0]))
	recording2 = read_wav(path.join(get_recording_dir(), files[1]))
	recording = recording1 + recording2
	original = read_wav(path.join(get_test_recording_dir(), 'tale.wav'))
	start, end = generate_audio_files["tale"]
	desired_speech = original[start + 20000:end - 20000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < 0.5


# test that speech interspersed with silence saves appropriately
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'star.wav')], indirect=['mock_stream'])
def test_pauses(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	files = sorted(os.listdir(get_recording_dir()))
	assert len(files) == 2 # the first section of speech is below the length threshold
	recording1 = read_wav(path.join(get_recording_dir(), files[0]))
	recording2 = read_wav(path.join(get_recording_dir(), files[1]))
	original = read_wav(path.join(get_test_recording_dir(), 'star.wav'))
	((start1, end1), (start2, end2)) = generate_audio_files["star"]
	desired_speech1 = original[start1 + 1000:end1 - 1000]
	desired_speech2 = original[start2 + 5000:end2 - 20000]
	assert desired_speech1 in recording1
	assert desired_speech2 in recording2
	assert (len(recording1) - len(desired_speech1)) / (config.get("num_bytes") * config.get("rate")) < 1.5
	assert (len(recording2) - len(desired_speech2)) / (config.get("num_bytes") * config.get("rate")) < .5


# test distinguishing speech from background noise
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'noise.wav')], indirect=['mock_stream'])
def test_noise(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'noise.wav'))
	start, end = generate_audio_files["noise"]
	desired_speech = original[start + 20000:end - 25000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < .5


# test separating multiple voices from silence
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+como.wav')], indirect=['mock_stream'])
def test_multivoice(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+como.wav'))
	start, end = generate_audio_files["multivoice"]
	desired_speech = original[start + 9000:end - 9000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < .5


# test separating multiple voices from background noise
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+como_noise.wav')], indirect=['mock_stream'])
def test_multivoice_noise(generate_audio_files, mock_stream, config):
	record.record(Queue(), config)
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+como_noise.wav'))
	start, end = generate_audio_files["multivoice_noise"]
	desired_speech = original[start + 15000:end - 15000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (config.get("num_bytes") * config.get("rate")) < .5