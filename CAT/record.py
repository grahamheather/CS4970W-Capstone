import pyaudio
import webrtcvad
from CAT import utilities
from CAT.settings import *


def open_stream():
	''' Opens audio recording stream

		Returns: the audio stream
		Return type: pyaudio.Stream
	'''

	audio_input = pyaudio.PyAudio()
	stream = audio_input.open(format=FORMAT,
							  channels=NUM_CHANNELS,
							  rate=RATE,
							  input=True,
							  start=False,
							  frames_per_buffer=VAD_FRAME_SIZE)
	stream.start_stream()
	return stream


def queue_audio_buffer(audio_buffer, file_queue):
	''' Saves and queues an audio buffer to a file

		Parameters:
			audio_buffer
				the audio buffer to save to the file
				type: list of byte strings
			file_queue
				queue to add the new filename to
	'''

	# CHECK IF THERE IS ENOUGH SPACE REMAINING
	# OTHERWISE SWITCH TO JUST PROCESSING, NO RECORDING

	# join segments of audio into a single byte string
	data = b''.join(segment for segment in audio_buffer)

	# save byte string to a file
	filename = utilities.save_to_file(data)

	# add the new file to the processing queue
	file_queue.put(filename)


def record(file_queue):
	''' Records and saves detected speech, discarding silence 
	
		Parameters:
			file_queue
				queue to add filenames of recordings to
	'''

	# set up
	stream = open_stream()
	vad = webrtcvad.Vad(VAD_LEVEL)

	last_speech = None # how many frames ago speech was detected (None indicates no recent speech)
	audio_buffer = [] # holds detected speech
	current_read_frames = 0 # indicates how many frames were just read

	while not stream.is_stopped(): # record continuously
		if not last_speech == None: # if there has been recent speech, read a small section to analyze
			audio = stream.read(VAD_FRAME_SIZE)
			current_read_frames = 1
		else: # if there has not been recent speech, only check for speech periodically
			audio = stream.read(VAD_FRAME_SIZE * PERIODIC_SAMPLE_FRAMES)
			current_read_frames = PERIODIC_SAMPLE_FRAMES

		if vad.is_speech(audio[-VAD_FRAME_BYTES:], RATE): # if speech has been detected
			last_speech = 0 # update that speech has been detected
			audio_buffer.append(audio) # add speech
			if len(audio_buffer) > MAX_SAMPLE_FRAMES: # if speech buffer is getting long
				queue_audio_buffer(audio_buffer, file_queue) # save incomplete speech sequence to file
				audio_buffer = [] # and clear buffer
		elif not last_speech == None: # otherwise if still possibily in a sequence of speech
			last_speech += 1 # update how long it has been since last speech
			audio_buffer.append(audio) # add this momentary silence to the buffer (to prevent choppy audio)

			if last_speech > MAX_SILENCE_FRAMES: # if the pause is long enough to indicate an end to speech
				if len(audio_buffer) - last_speech > MIN_SAMPLE_FRAMES: # only save if the detected speech is long enough
					audio_buffer = audio_buffer[:-last_speech] # only save speech until last detected speech (discard silence)
					queue_audio_buffer(audio_buffer, file_queue) 

				# reset to no speech recently detected
				audio_buffer = []
				last_speech = None