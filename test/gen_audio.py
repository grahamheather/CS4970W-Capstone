# Automatically generates the testing audio files
# Note that this functionality requires Internet acess

from os import path, remove
from pydub import AudioSegment
from gtts import gTTS
from CAT.record import MILLISECONDS_PER_SECOND, RATE, MAX_SAMPLE_LENGTH, MIN_SAMPLE_LENGTH, MAX_SILENCE_LENGTH, VAD_FRAME_MS, PERIODIC_SAMPLE_RATE, NUM_BYTES

MARGIN = 2 * VAD_FRAME_MS # in milliseconds
LARGER_MARGIN = PERIODIC_SAMPLE_RATE * MILLISECONDS_PER_SECOND

def generate_silence(filename):
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND)
	silence = silence.set_frame_rate(RATE)
	silence.export(filename, format="wav")

	return None

def generate_short(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	short = gTTS("hello")
	short.save("{}.mp3".format(file_path))
	short = AudioSegment.from_mp3("{}.mp3".format(file_path))
	remove("{}.mp3".format(file_path))

	# add silence and save
	short = short[:MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN]
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND)
	silence = silence.set_frame_rate(RATE)
	short = short + silence
	short.export(filename, format="wav")

	return None

def generate_short_long(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	short_file = gTTS("hello")
	short_file.save("{}_short.mp3".format(file_path))
	short_audio = AudioSegment.from_mp3("{}_short.mp3".format(file_path))
	remove("{}_short.mp3".format(file_path))
	long_file = gTTS("How are you doing?")
	long_file.save("{}_long.mp3".format(file_path))
	long_audio = AudioSegment.from_mp3("{}_long.mp3".format(file_path))
	remove("{}_long.mp3".format(file_path))

	# fix lengths
	if len(short_audio) > MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN:
		short_audio = short_audio[:MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN]
	while len(long_audio) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		long_audio = long_audio + long_audio

	# add silence and save
	beginning = short_audio + AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = beginning + long_audio + AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio.export(filename, format="wav")

	start = len(beginning) * NUM_BYTES * RATE / MILLISECONDS_PER_SECOND
	end = (len(beginning) + len(long_audio)) * NUM_BYTES * RATE / MILLISECONDS_PER_SECOND

	return (int(start), int(end))

def generate_normal(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	file = gTTS("In a hole in the ground there lived a hobbit.")
	file.save("{}.mp3".format(file_path))
	speech = AudioSegment.from_mp3("{}.mp3".format(file_path))
	remove("{}.mp3".format(file_path))

	# fix lengths
	while len(speech) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence and save
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = speech + silence
	audio.export(filename, format="wav")

	start = 0
	end = len(speech) * NUM_BYTES * RATE / MILLISECONDS_PER_SECOND
	return (int(start), int(end))



def generate_all_audio(folder):
	stats = {}
	stats["silence"] = generate_silence(path.join(folder, "silence.wav"))
	stats["hello"] = generate_short(path.join(folder, "hello.wav"))
	stats["hello+how"] = generate_short_long(path.join(folder, "hello+how.wav"))
	stats["ground"] = generate_normal(path.join(folder, "ground.wav"))

	return stats



if __name__ == "__main__":
	# FIX HARD-CODED FILENAMES
	#generate_silence("test/test_recordings/silence.wav")
	#generate_short("test/test_recordings/hello.wav")
	print("NOT IMPLEMENTED")