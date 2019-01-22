import collections
import datetime

import pyaudio
import wave
import webrtcvad

# universal constants
MILLISECONDS_PER_SECOND = 1000

# audio recording settings
FORMAT = pyaudio.paInt16 # WebRTC VAD only accepts 16-bit audio
NUM_BYTES = 2 # 16 bits in format = 2 bytes in format
CHANNELS = 1 # WebRTC VAD only accepts mono audio
RATE = 48000 # WebRTC VAD only accepts 8000, 16000, 32000 or 48000 Hz
FRAME_MS = 30 # WebRTC VAD only accepts frames of 10, 20, or 30 ms
FRAME_SIZE = int(RATE * FRAME_MS / MILLISECONDS_PER_SECOND)
FRAME_BYTES = FRAME_SIZE * NUM_BYTES

# settings based on system timing and situation
PERIODIC_SAMPLE_RATE = 1  # how often to check when no speech has been detected, in seconds
MIN_SAMPLE_LENGTH = 5 # smallest sample to save, in seconds
MAX_SAMPLE_LENGTH = 30 # largest sample to save (larger ones will be split), in seconds
MAX_SILENCE_LENGTH = 2 # largest length of silence to include in a single sample

# calculated from system settings
PERIODIC_SAMPLE_FRAMES = int(PERIODIC_SAMPLE_RATE * MILLISECONDS_PER_SECOND / FRAME_MS)
MIN_SAMPLE_FRAMES = int(MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)
MAX_SAMPLE_FRAMES = int(MAX_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)
MAX_SILENCE_FRAMES = int(MAX_SILENCE_LENGTH * MILLISECONDS_PER_SECOND / FRAME_MS)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ADD LOGGING
# ADD COMMENTS
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def open_stream():
	audio_input = pyaudio.PyAudio()
	stream = audio_input.open(format=FORMAT,
							  channels=CHANNELS,
							  rate=RATE,
							  input=True,
							  start=False,
							  frames_per_buffer=FRAME_SIZE)
	stream.start_stream()
	return stream


def save_to_file(data):
	# CHECK IF THERE IS ENOUGH SPACE REMAINING
	# OTHERWISE SWITCH TO JUST PROCESSING, NO RECORDING
	wave_file = wave.open("audio{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")), 'wb')
	wave_file.setnchannels(CHANNELS)
	wave_file.setsampwidth(NUM_BYTES)
	wave_file.setframerate(RATE)
	wave_file.writeframes(data)
	wave_file.close()


def record():
	stream = open_stream()
	vad = webrtcvad.Vad(1)

	last_speech = None
	audio_buffer = collections.deque()
	num_frames = 0
	current_read_frames = 0

	while True:
		if not last_speech == None:
			audio = stream.read(FRAME_SIZE)
			current_read_frames = 1
		else:
			audio = stream.read(FRAME_SIZE * PERIODIC_SAMPLE_FRAMES)
			current_read_frames = PERIODIC_SAMPLE_FRAMES

		if vad.is_speech(audio[-FRAME_BYTES:], RATE):
			# TAKE LOCK
			last_speech = 0
			audio_buffer.append(audio)
			if len(audio_buffer) > MAX_SAMPLE_FRAMES:
				save_to_file(audio_buffer)
				audio_buffer.clear()
		elif not last_speech == None:
			last_speech += 1
			if last_speech > MAX_SILENCE_FRAMES:
				if last_speech - len(audio_buffer) > MIN_SAMPLE_FRAMES:
					for i in range(last_speech):
						audio_buffer.pop()
					data = b''.join(segment for segment in audio_buffer)
					save_to_file(data)
				audio_buffer.clear()
				last_speech = None
				# RELEASE LOCK
				

if __name__ == '__main__':
	record()