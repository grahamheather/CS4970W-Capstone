import collections
import datetime
from os import path

import pyaudio
import wave
import webrtcvad

# universal constants
MILLISECONDS_PER_SECOND = 1000

# audio recording settings
VAD_LEVEL = 2 # "integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive." -py-webrtcvad docs
FORMAT = pyaudio.paInt16 # WebRTC VAD only accepts 16-bit audio
NUM_BYTES = 2 # 16 bits in format = 2 bytes in format
CHANNELS = 1 # WebRTC VAD only accepts mono audio
RATE = 48000 # WebRTC VAD only accepts 8000, 16000, 32000 or 48000 Hz
FRAME_MS = 30 # WebRTC VAD only accepts frames of 10, 20, or 30 ms
FRAME_SIZE = int(RATE * FRAME_MS / MILLISECONDS_PER_SECOND)
FRAME_BYTES = FRAME_SIZE * NUM_BYTES

# settings based on system timing and situation
PERIODIC_SAMPLE_RATE = .5  # how often to check when no speech has been detected, in seconds
MIN_SAMPLE_LENGTH = .75 # smallest sample to save, in seconds
MAX_SAMPLE_LENGTH = 30 # largest sample to save (larger ones will be split), in seconds
MAX_SILENCE_LENGTH = .5 # largest length of silence to include in a single sample

# calculated from system settings
PERIODIC_SAMPLE_FRAMES = int(PERIODIC_SAMPLE_RATE * MILLISECONDS_PER_SECOND / FRAME_MS)
MIN_SAMPLE_FRAMES = int(MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)
MAX_SAMPLE_FRAMES = int(MAX_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)
MAX_SILENCE_FRAMES = int(MAX_SILENCE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)


def open_stream():
	''' Opens audio recording stream

		Returns: the audio stream
		Return type: pyaudio.Stream
	'''

	audio_input = pyaudio.PyAudio()
	stream = audio_input.open(format=FORMAT,
							  channels=CHANNELS,
							  rate=RATE,
							  input=True,
							  start=False,
							  frames_per_buffer=FRAME_SIZE)
	stream.start_stream()
	return stream


def save_to_file(audio_buffer):
	''' Saves an audio buffer to a file

		Parameters:
			audio_buffer
				the audio buffer to save to the file
				type: list of byte strings
	'''

	# CHECK IF THERE IS ENOUGH SPACE REMAINING
	# OTHERWISE SWITCH TO JUST PROCESSING, NO RECORDING

	# join segments of audio into a single byte string
	data = b''.join(segment for segment in audio_buffer)

	# save file with unique name indicating date and time
	wave_file = wave.open(path.join("CAT", "recordings", "audio{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"))), 'wb')
	wave_file.setnchannels(CHANNELS)
	wave_file.setsampwidth(NUM_BYTES)
	wave_file.setframerate(RATE)
	wave_file.writeframes(data)
	wave_file.close()


def record():
	''' Records and saves detected speech, discarding silence '''

	# set up
	stream = open_stream()
	vad = webrtcvad.Vad(VAD_LEVEL)

	last_speech = None # how many frames ago speech was detected (None indicates no recent speech)
	audio_buffer = [] # holds detected speech
	current_read_frames = 0 # indicates how many frames were just read

	while not stream.is_stopped(): # record continuously
		if not last_speech == None: # if there has been recent speech, read a small section to analyze
			audio = stream.read(FRAME_SIZE)
			current_read_frames = 1
		else: # if there has not been recent speech, only check for speech periodically
			audio = stream.read(FRAME_SIZE * PERIODIC_SAMPLE_FRAMES)
			current_read_frames = PERIODIC_SAMPLE_FRAMES

		if vad.is_speech(audio[-FRAME_BYTES:], RATE): # if speech has been detected
			# TAKE LOCK

			last_speech = 0 # update that speech has been detected
			audio_buffer.append(audio) # add speech
			if len(audio_buffer) > MAX_SAMPLE_FRAMES: # if speech buffer is getting long
				save_to_file(audio_buffer) # save incomplete speech sequence to file
				audio_buffer = [] # and clear buffer
		elif not last_speech == None: # otherwise if still possibily in a sequence of speech
			last_speech += 1 # update how long it has been since last speech
			audio_buffer.append(audio) # add this momentary silence to the buffer (to prevent choppy audio)

			if last_speech > MAX_SILENCE_FRAMES: # if the pause is long enough to indicate an end to speech
				if len(audio_buffer) - last_speech > MIN_SAMPLE_FRAMES: # only save if the detected speech is long enough
					audio_buffer = audio_buffer[:-last_speech] # only save speech until last detected speech (discard silence)
					save_to_file(audio_buffer) 

				# reset to no speech recently detected
				audio_buffer = []
				last_speech = None

				# RELEASE LOCK


if __name__ == '__main__':
	record()