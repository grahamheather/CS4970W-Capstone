# Automatically generates the testing audio files
# Note that this functionality requires Internet acess

from os import path, remove
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from gtts import gTTS
from CAT import settings

settings = settings.Config()
# conglomerate all relevant settings here, so they can be hard-coded or overridden for tests more easily
NUM_BYTES = settings.get("num_bytes")
RATE = settings.get("rate")
MILLISECONDS_PER_SECOND = settings.get("milliseconds_per_second")
MIN_SAMPLE_LENGTH = settings.get("min_sample_length")
MAX_SAMPLE_LENGTH = settings.get("max_sample_length")
MAX_SILENCE_LENGTH = settings.get("max_silence_length")


BITS_PER_BYTE = 8

MARGIN = 2 * settings.get("vad_frame_ms") # in milliseconds
LARGER_MARGIN = settings.get("periodic_sample_rate") * MILLISECONDS_PER_SECOND

def generate_speech(text, lang, file_path):
	speech_file = gTTS(text, lang=lang)
	speech_file.save("{}.mp3".format(file_path))
	speech = AudioSegment.from_mp3("{}.mp3".format(file_path))
	remove("{}.mp3".format(file_path))
	return speech

def milliseconds_to_bytes(n):
	return int(n * NUM_BYTES * RATE / MILLISECONDS_PER_SECOND)


def generate_record_silence(filename):
	silence = AudioSegment.silent(duration=MAX_SAMPLE_LENGTH*MILLISECONDS_PER_SECOND)
	silence = silence.set_frame_rate(RATE)
	silence.export(filename, format="wav")

	return None


def generate_record_short(filename):
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


def generate_record_short_long(filename):
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


def generate_record_normal(filename):
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


def generate_record_too_long(filename):
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


def generate_record_pauses(filename):
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


def generate_record_noise(filename):
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


def generate_record_multivoice(filename):
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


def generate_record_multivoice_noise(filename):
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


def generate_test_record_audio(folder):
	stats = {}
	stats["silence"] = generate_record_silence(path.join(folder, "silence.wav"))
	stats["hello"] = generate_record_short(path.join(folder, "hello.wav"))
	stats["hello+how"] = generate_record_short_long(path.join(folder, "hello+how.wav"))
	stats["ground"] = generate_record_normal(path.join(folder, "ground.wav"))
	stats["tale"] = generate_record_too_long(path.join(folder, "tale.wav"))
	stats["star"] = generate_record_pauses(path.join(folder, "star.wav"))
	stats["noise"] = generate_record_noise(path.join(folder, "noise.wav"))
	stats["multivoice"] = generate_record_multivoice(path.join(folder, "hello+como.wav"))
	stats["multivoice_noise"] = generate_record_multivoice_noise(path.join(folder, "hello+como_noise.wav"))

	return stats


def generate_diarization_normal(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 = generate_speech("Hello, how are you?", 'en', file_path)
	speech2 = generate_speech("Hello, how are you?", 'es', file_path)

	# add silence and save
	silence = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND - MARGIN).set_frame_rate(RATE)
	audio = speech1 + silence + speech2
	audio.export(filename, format="wav")

	start1 = 0
	end1 = milliseconds_to_bytes(len(speech1))
	start2 = end1 + milliseconds_to_bytes(len(silence))
	end2 = start2 + milliseconds_to_bytes(len(speech2))

	return ((start1, end1), (start2, end2))


def generate_diarization_noise(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 = generate_speech("Hello, how are you?", 'en', file_path)
	speech2 = generate_speech("Hello, how are you?", 'es', file_path)

	# add silence
	silence = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND - MARGIN).set_frame_rate(RATE)
	audio = speech1 + silence + speech2

	# add noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=len(audio))
	noise = noise - 30
	audio = audio.overlay(noise)

	# save
	audio.export(filename, format="wav")

	start1 = 0
	end1 = milliseconds_to_bytes(len(speech1))
	start2 = end1 + milliseconds_to_bytes(len(silence))
	end2 = start2 + milliseconds_to_bytes(len(speech2))

	return ((start1, end1), (start2, end2))


def generate_diarization_single(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("Hello, how are you?", 'en', file_path)

	# save
	speech.export(filename, format="wav")

	start = 0
	end = milliseconds_to_bytes(len(speech))

	return (start, end)


def generate_diarization_single_noise(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("Hello, how are you?", 'en', file_path)

	# add noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=len(speech))
	noise = noise - 30
	audio = speech.overlay(noise)

	# save
	audio.export(filename, format="wav")

	start = 0
	end = milliseconds_to_bytes(len(speech))

	return (start, end)


def generate_test_diarization_audio(folder):
	stats = {}
	stats["normal"] = generate_diarization_normal(path.join(folder, "diarization_normal.wav"))
	stats["noise"] = generate_diarization_noise(path.join(folder, "diarization_noise.wav"))
	stats["single"] = generate_diarization_single(path.join(folder, "diarization_single.wav"))
	stats["single_noise"] = generate_diarization_single_noise(path.join(folder, "diarization_single_noise.wav"))

	return stats


def generate_speaker_id_same_recording(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech = generate_speech("Hello, how are you?", 'en', file_path)

	# save
	speech.export(filename, format="wav")


def generate_speaker_id_two_speakers(filename):
	file_path, file_extension = path.splitext(filename)

	# generate text-to-speech
	speech1 = generate_speech("Hello, how are you?", 'en', file_path)
	speech2 = generate_speech("Hello, how are you?", 'es', file_path)

	# add silence
	silence = AudioSegment.silent(duration=MAX_SILENCE_LENGTH*MILLISECONDS_PER_SECOND - MARGIN).set_frame_rate(RATE)
	audio = speech1 + silence + speech2

	# save
	audio.export(filename, format="wav")


def generate_speaker_id_noise_audio(filename):
	duration_in_ms = 20

	# generate noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=duration_in_ms)

	# save
	noise.export(filename, format="wav")

	return noise._data


def generate_test_speaker_id_audio(folder):
	stats = {}
	generate_speaker_id_same_recording(path.join(folder, "speaker_id_same_recording.wav"))
	generate_speaker_id_two_speakers(path.join(folder, "speaker_id_two_speakers.wav"))
	stats["noise"] = generate_speaker_id_noise_audio(path.join(folder, "speaker_id_noise.wav"))

	return stats


def generate_utilities_read_file_audio(filename):
	duration_in_ms = 20

	# generate noise
	noise = WhiteNoise(sample_rate=RATE, bit_depth=NUM_BYTES*BITS_PER_BYTE).to_audio_segment(duration=duration_in_ms)

	# save
	noise.export(filename, format="wav")

	return noise._data


def generate_test_utilities_audio(folder):
	stats = {}
	stats["read_file"] = generate_utilities_read_file_audio(path.join(folder, "utilities_read_file.wav"))

	return stats

