import pytest

# supporting libraries
import pyaudio
import wave
from os import path
import os

# file under test
from CAT import record


# UTILITY FUNCTIONS
def get_recording_dir():
	return path.join('CAT', 'recordings')

def get_test_recording_dir():
	return path.join('test', 'test_recordings')

def read_wav(filename):
	wave_file = wave.open(filename, 'r')
	return wave_file.readframes(wave_file.getnframes())


# FIXTURES

# fixture wrapping a wave file reader to the microphone input reader
@pytest.fixture()
def mock_stream(request, monkeypatch):
	class MockStream:
		i = 0 # track how many frames have been read

		def __init__(self, filename):
			self.wave_file = wave.open(filename, 'r')
			self.n = self.wave_file.getnframes()
			assert self.wave_file.getnchannels() == record.CHANNELS
			assert self.wave_file.getsampwidth() == record.NUM_BYTES
			assert self.wave_file.getframerate() == record.RATE

		def read(self, frame_size):
			self.i = self.i + frame_size
			return self.wave_file.readframes(frame_size)
			

		def is_stopped(self):
			# note that this might cut off the end of the audio file
			return (self.i >= self.n - record.FRAME_SIZE * record.PERIODIC_SAMPLE_FRAMES)


	def mockreturn():
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
def test_open_stream():
	result = record.open_stream()
	assert type(result) == pyaudio.Stream
	
# test saving to file
def test_save_to_file():
	wave_file = wave.open(path.join(get_test_recording_dir(), 'hello.wav'), 'r')
	audio_buffer = [wave_file.readframes(record.FRAME_SIZE) for i in range( int(wave_file.getnframes() / record.FRAME_SIZE + .5) ) ]
	record.save_to_file(audio_buffer)
	assert len(os.listdir(get_recording_dir())) == 1

	saved_file = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	wave_file.rewind()
	assert saved_file == wave_file.readframes(wave_file.getnframes())

# test saving a file if the disk is full

# test that feeding only silence will not save a file
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'silence.wav')], indirect=['mock_stream'])
def test_silence(mock_stream):
	record.record()
	assert os.listdir(get_recording_dir()) == []

# test that speech less than the min sample length will not save a file
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello.wav')], indirect=['mock_stream'])
def test_short(mock_stream):
	record.record()
	assert os.listdir(get_recording_dir()) == []

# test that speech less than min sample length will not save a file but future speech will save a file
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+how.wav')], indirect=['mock_stream'])
def test_short_long(mock_stream):
	record.record()
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+how.wav'))
	desired_speech = original[230000:335000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < 0.5

# test that speech between the min and max sample lengths saves a single file
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'ground.wav')], indirect=['mock_stream'])
def test_normal(mock_stream):
	record.record()
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'ground.wav'))
	desired_speech = original[:230000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < 0.5

# test that speech longer than the max sample length will save multiple files
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'tale.wav')], indirect=['mock_stream'])
def test_too_long(mock_stream):
	record.record()
	files = sorted(os.listdir(get_recording_dir()))
	assert len(files) == 2
	recording1 = read_wav(path.join(get_recording_dir(), files[0]))
	recording2 = read_wav(path.join(get_recording_dir(), files[1]))
	recording = recording1 + recording2
	original = read_wav(path.join(get_test_recording_dir(), 'tale.wav'))
	desired_speech = original[2870000:7000000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < .5

# test that speech interspersed with silence saves appropriately
# (check file length and contents)
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'star.wav')], indirect=['mock_stream'])
def test_pauses(mock_stream):
	record.record()
	files = sorted(os.listdir(get_recording_dir()))
	assert len(files) == 2 # the first section of speech is below the length threshold
	recording2 = read_wav(path.join(get_recording_dir(), files[0]))
	recording3 = read_wav(path.join(get_recording_dir(), files[1]))
	original = read_wav(path.join(get_test_recording_dir(), 'star.wav'))
	desired_speech2 = original[2040000:2160000]
	desired_speech3 = original[2640000:2800000]
	assert desired_speech2 in recording2
	assert desired_speech3 in recording3
	assert (len(recording2) - len(desired_speech2)) / (record.NUM_BYTES * record.RATE) < .5
	assert (len(recording3) - len(desired_speech3)) / (record.NUM_BYTES * record.RATE) < .5

# test distinguishing speech from background noise
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'noise.wav')], indirect=['mock_stream'])
def test_noise(mock_stream):
	record.record()
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'noise.wav'))
	desired_speech = original[1250000:1470000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < .5

# test separating multiple voices from silence
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+como.wav')], indirect=['mock_stream'])
def test_multivoice(mock_stream):
	record.record()
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+como.wav'))
	desired_speech = original[1640000:1790000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < .5

# test separating multiple voices from background noise
@pytest.mark.parametrize('mock_stream', [path.join(get_test_recording_dir(), 'hello+como_noise.wav')], indirect=['mock_stream'])
def test_multivoice(mock_stream):
	record.record()
	assert len(os.listdir(get_recording_dir())) == 1
	recording = read_wav(path.join(get_recording_dir(), os.listdir(get_recording_dir())[0]))
	original = read_wav(path.join(get_test_recording_dir(), 'hello+como_noise.wav'))
	desired_speech = original[1645000:1785000]
	assert desired_speech in recording
	assert (len(recording) - len(desired_speech)) / (record.NUM_BYTES * record.RATE) < .5