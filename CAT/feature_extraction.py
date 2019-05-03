import sys

def extract_features(filename):
	''' Extracts features from a file of audio data
		Parameters:
			filename
				str, the name of the file to extract features from
		Returns:
			filename to extracted features
	'''
	extract_phonation_features(filename)
	extract_articulation_features(filename)

	return "VERY IMPORTANT FEATURES"

def extract_phonation_features(filename):
	'''	Extracts phonation features from a file of audio data
		Parameters:
			filename
		Returns:
			filename to extracted features
	'''
	sys.argv = [filename, "phonation_features.txt", "static"]
	exec(open("../../DisVoice/articulation/articulation.py").read())

def extract_articulation_features(filename):
	'''	Extracts phonation features from a file of audio data
		Parameters:
			filename
		Returns:
			filename to extracted features
	'''
	sys.argv = [filename, "articulation_features.txt", "static"]
	exec(open("../../DisVoice/articulation/articulation.py").read())

extract_features("../../DisVoice/articulation/001_ddk_PCGITA.wav")
