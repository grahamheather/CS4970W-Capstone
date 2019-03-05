# Automatically generates the testing audio files
# Note that this functionality requires Internet acess

from os import path, remove
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from gtts import gTTS
from CAT.record import MILLISECONDS_PER_SECOND, RATE, MAX_SAMPLE_LENGTH, MIN_SAMPLE_LENGTH, MAX_SILENCE_LENGTH, VAD_FRAME_MS, PERIODIC_SAMPLE_RATE, NUM_BYTES

BITS_PER_BYTE = 8

MARGIN = 2 * VAD_FRAME_MS # in milliseconds
LARGER_MARGIN = PERIODIC_SAMPLE_RATE * MILLISECONDS_PER_SECOND

def generate_speech(text, lang, file_path):
	speech_file = gTTS(text, lang=lang)
	speech_file.save("{}.mp3".format(file_path))
	speech = AudioSegment.from_mp3("{}.mp3".format(file_path))
	remove("{}.mp3".format(file_path))
	return speech

def milliseconds_to_bytes(n):
	return int(n * NUM_BYTES * RATE / MILLISECONDS_PER_SECOND)


def generate_silence(filename):
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND)
	silence = silence.set_frame_rate(RATE)
	silence.export(filename, format="wav")

	return None


def generate_short(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	short = generate_speech("hello", "en", file_path)

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
	short_audio = generate_speech("hello", "en", file_path)
	long_audio = generate_speech("How are you doing?", 'en', file_path)

	# fix lengths
	if len(short_audio) > MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN:
		short_audio = short_audio[:MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN]
	while len(long_audio) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		long_audio = long_audio + long_audio

	# add silence and save
	beginning = short_audio + AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = beginning + long_audio + AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio.export(filename, format="wav")

	start = milliseconds_to_bytes(len(beginning))
	end = milliseconds_to_bytes(len(beginning) + len(long_audio))

	return (start, end)


def generate_normal(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("In a hole in the ground there lived a hobbit.", "en", file_path)

	# fix lengths
	while len(speech) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence and save
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = speech + silence
	audio.export(filename, format="wav")

	start = 0
	end = milliseconds_to_bytes(len(speech))
	return (start, end)


def generate_too_long(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way – in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.",
				"en", file_path)

	# fix lengths
	while len(speech) < MAX_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence and save
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = speech + silence
	audio.export(filename, format="wav")

	start = 0
	end = milliseconds_to_bytes(len(speech))
	return (start, end)


def generate_pauses(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 = generate_speech("Do or do not.", "en", file_path)
	speech2 = generate_speech("There is no try.", "en", file_path)
	speech3 = generate_speech("May the force be with you.", "en", file_path)

	# fix lengths
	if len(speech1) > MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN:
		speech1 = speech1[:MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND - MARGIN]
	while len(speech2) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech2 = speech2 + speech2
	while len(speech3) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech3 = speech3 + speech3

	# add silence and save
	silence_pre1 = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	silence_12 = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	silence_23 = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	silence_post3 = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND).set_frame_rate(RATE)
	audio = silence_pre1 + speech1 + silence_12 + speech2 + silence_23 + speech3 + silence_post3
	audio.export(filename, format="wav")

	start2 = milliseconds_to_bytes(len(silence_pre1) + len(speech1) + len(silence_12))
	end2 = start2 + milliseconds_to_bytes(len(speech2))
	start3 = end2 + milliseconds_to_bytes(len(silence_23))
	end3 = start3 + milliseconds_to_bytes(len(speech3))

	return ((start2, end2), (start3, end3))


def generate_noise(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("How are you doing today?", "en", file_path)

	# fix lengths
	while len(speech) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	audio = silence + speech + silence

	# add noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=len(audio))
	noise = noise - 30
	audio = audio.overlay(noise)

	# save
	audio.export(filename, format="wav")

	start = milliseconds_to_bytes(len(silence))
	end = milliseconds_to_bytes(len(silence) + len(speech))

	return (start, end)


def generate_multivoice(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 = generate_speech("Hello", "en", file_path)
	speech2 = generate_speech("¿Cómo se va?", "es", file_path)
	speech = speech1 + speech2

	# fix lengths
	while len(speech) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	audio = silence + speech + silence

	# add noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=len(audio))
	noise = noise - 30
	audio = audio.overlay(noise)

	# save
	audio.export(filename, format="wav")

	start = milliseconds_to_bytes(len(silence))
	end = milliseconds_to_bytes(len(silence) + len(speech))

	return (start, end)


def generate_multivoice_noise(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 =  generate_speech("Hello", "en", file_path)
	speech2 = generate_speech("¿Cómo se va?", "es", file_path)
	speech = speech1 + speech2

	# fix lengths
	while len(speech) < MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND + LARGER_MARGIN:
		speech = speech + speech

	# add silence and save
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND + MARGIN).set_frame_rate(RATE)
	audio = silence + speech + silence
	audio.export(filename, format="wav")

	start = milliseconds_to_bytes(len(silence))
	end = milliseconds_to_bytes(len(silence) + len(speech))

	return (start, end)


def generate_all_audio(folder):
	stats = {}
	stats["silence"] = generate_silence(path.join(folder, "silence.wav"))
	stats["hello"] = generate_short(path.join(folder, "hello.wav"))
	stats["hello+how"] = generate_short_long(path.join(folder, "hello+how.wav"))
	stats["ground"] = generate_normal(path.join(folder, "ground.wav"))
	stats["tale"] = generate_too_long(path.join(folder, "tale.wav"))
	stats["star"] = generate_pauses(path.join(folder, "star.wav"))
	stats["noise"] = generate_noise(path.join(folder, "noise.wav"))
	stats["multivoice"] = generate_multivoice(path.join(folder, "hello+como.wav"))
	stats["multivoice_noise"] = generate_multivoice_noise(path.join(folder, "hello+como_noise.wav"))

	return stats