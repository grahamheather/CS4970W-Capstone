from CAT import diarization
from CAT import speaker_reid
from CAT import utilities
from CAT.settings import *


def identify_speakers(filename, speaker_dictionary, speaker_dictionary_lock):
	''' Splits a single audio file by speaker and identifies speakers
		
		Parameters:
			filename
				str, the name of the file to analyze
			speaker_dictionary
				dict, dictionary to store statistics about each speaker in
			speaker_dictionary_lock
				a lock so that multiple processes do not try to read/write/update/delete speakers concurrently
		Returns:
			[(str, str)], list of tuples of (filename, speaker ID)
	'''

	files = []
	segments_by_speaker, speaker_means, speaker_covariances = diarization.split_by_speaker(filename)
	speaker_id_map = {}
	for speaker in segments_by_speaker:
		speaker_id_map[speaker] = speaker_reid.identify_speaker(speaker_means[speaker, :], speaker_covariances[speaker, :, :], speaker_dictionary, speaker_dictionary_lock)
	for speaker in segments_by_speaker:
		for segment in segments_by_speaker[speaker]:
			filename = utilities.save_to_file(segment)
			files.append((filename, speaker_id_map[speaker]))

	return files