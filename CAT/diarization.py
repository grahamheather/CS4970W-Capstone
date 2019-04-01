import collections
from pyAudioAnalysis import audioSegmentation
from CAT import utilities


def split_by_speaker(filename, config):
	''' Splits a file of audio into segments identified by speaker

		Parameters:
			filename
				string, the name of the audio file
			config
				CAT.settings.Config - all settings. associated with the program

		Returns:
			{
				speaker_id: list of windows of audio data (list of byte strings)
			},
			list of multi-dimensional means of the normal PDF associated with each speaker,
			list of covariance matrices of the normal PDF associated with each speaker
	'''

	# LDA is disabled so that all speakers are analyzed in the same space
	# and all clusters across all speaker identifications are roughly
	# Gaussian in that space
	speaker_detected_by_window, speaker_means, speaker_covariances = audioSegmentation.speakerDiarization(filename, config.get("max_speakers"), lda_dim=0)

	# calculate necessary stats on labelled windows
	WINDOW_LENGTH = .2 # in seconds
	LENGTH_OF_WINDOW_IN_FRAMES = int(config.get("rate") * WINDOW_LENGTH)
	LENGTH_OF_WINDOW_IN_BYTES = LENGTH_OF_WINDOW_IN_FRAMES * config.get("num_channels") * config.get("num_bytes")

	# open file
	audio = utilities.read_file(filename)

	# split file into multiple segments based on speaker and sort by speaker
	segments_by_speaker = collections.defaultdict(list)
	previous_speaker = None
	for window_index in range(len(speaker_detected_by_window)):
		previous_speaker = speaker_detected_by_window[window_index - 1] if window_index > 0 else None
		speaker = int(speaker_detected_by_window[window_index])
		start_frame = LENGTH_OF_WINDOW_IN_BYTES * window_index
		
		window = audio[start_frame:start_frame + LENGTH_OF_WINDOW_IN_BYTES]
		if speaker == previous_speaker:
			segments_by_speaker[speaker][-1] += window
		else:
			segments_by_speaker[speaker].append(window)

	return segments_by_speaker, speaker_means, speaker_covariances