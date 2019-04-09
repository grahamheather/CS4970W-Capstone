import pyaudio
import webrtcvad
from CAT import utilities

def open_stream(config):
	''' Opens audio recording stream
		Parameters:
			config
				CAT.settings.Config - all settings associated with the program

		Returns: the audio stream
		Return type: pyaudio.Stream
	'''

	audio_input = pyaudio.PyAudio()
	stream = audio_input.open(format=config.get("format"),
							  channels=config.get("num_channels"),
							  rate=config.get("rate"),
							  input=True,
							  start=False,
							  frames_per_buffer=config.get("vad_frame_size")
	)
	stream.start_stream()
	return stream


def queue_audio_buffer(audio_buffer, file_queue, config):
	''' Saves and queues an audio buffer to a file

		Parameters:
			audio_buffer
				the audio buffer to save to the file
				type: list of byte strings
			file_queue
				queue to add the new filename to
			config
				CAT.settings.Config - all settings associated with the program
	'''

	# join segments of audio into a single byte string
	data = b''.join(segment for segment in audio_buffer)

	try:
		# save byte string to a file
		filename = utilities.save_to_file(data, config)
	except IOError:
		return

	# add the new file to the processing queue
	file_queue.put(filename)


def record(file_queue, config, threads_ready_to_update, settings_update_event):
	''' Records and saves detected speech, discarding silence
	
		Parameters:
			file_queue
				queue to add filenames of recordings to
			config
				CAT.settings.Config - all settings associated with the program
			threads_ready_to_update
				multiprocessing.Semaphore - indicates how many threads are currently ready for a settings update
			settings_update_event
				multiprocessing.Event - indicates whether a settings update is occuring (cleared - occuring, set - not occurring)
	'''

	# acquire the semaphore indicating thread is starting
	threads_ready_to_update.acquire()

	# set up
	stream = open_stream(config)
	vad = webrtcvad.Vad(config.get("vad_level"))

	last_speech = None # how many frames ago speech was detected (None indicates no recent speech)
	audio_buffer = [] # holds detected speech
	current_read_frames = 0 # indicates how many frames were just read

	while not stream.is_stopped(): # record continuously
		if not last_speech == None: # if there has been recent speech, read a small section to analyze
			audio = stream.read(config.get("vad_frame_size"))
			current_read_frames = 1
		else: # if there has not been recent speech, only check for speech periodically
			audio = stream.read(config.get("vad_frame_size") * config.get("periodic_sample_frames"))
			current_read_frames = config.get("periodic_sample_frames")

		if vad.is_speech(audio[-config.get("vad_frame_bytes"):], config.get("rate")): # if speech has been detected
			last_speech = 0 # update that speech has been detected
			audio_buffer.append(audio) # add speech
			if len(audio_buffer) > config.get("max_sample_frames"): # if speech buffer is getting long
				queue_audio_buffer(audio_buffer, file_queue, config) # save incomplete speech sequence to file
				audio_buffer = [] # and clear buffer
		elif not last_speech == None: # otherwise if still possibily in a sequence of speech
			last_speech += 1 # update how long it has been since last speech
			audio_buffer.append(audio) # add this momentary silence to the buffer (to prevent choppy audio)

			if last_speech > config.get("max_silence_frames"): # if the pause is long enough to indicate an end to speech
				if len(audio_buffer) - last_speech > config.get("min_sample_frames"): # only save if the detected speech is long enough
					audio_buffer = audio_buffer[:-last_speech] # only save speech until last detected speech (discard silence)
					queue_audio_buffer(audio_buffer, file_queue, config) 

				# reset to no speech recently detected
				audio_buffer = []
				last_speech = None
		else:
			# no speech is detected now and no speech has been detected recently
			# so this is a good time for a settings update
			threads_ready_to_update.release() # signal that this thread is ready to update settings
			settings_update_event.wait() # do not attempt to re-acquire the semaphore until the settings update is complete
			threads_ready_to_update.acquire() # signal that this thread is no longer ready to update settings