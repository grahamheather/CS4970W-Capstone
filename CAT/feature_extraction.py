import os
import csv
import json
from pyAudioAnalysis import audioFeatureExtraction as afe
from pyAudioAnalysis import audioBasicIO



def extract_features(filename):
	''' Extracts features from a file of audio data
		Parameters:
			filename
				str, the name of the file to extract features from
		Returns:
			filename to extracted features
	'''
	#base name of output file
	output_filename = "computed_features_file"
	#base list of feature names for labelng with json
	'''
	feature_names = 	("Zero_Crosing_Rate","Energy","Entropy_of_Energy","Spectral_Centroid","Spectral_Spread",
	          "Spectral_Entropy","Spectral_Flux", "Spectral_Rollof", "MFCC_1", "MFCC_2", "MFCC_3",
	          "MFCC_4", "MFCC_5", "MFCC_6", "MFCC_7", "MFCC_8", "MFCC_9", "MFCC_10", "MFCC_11", "MFCC_12", "MFCC_13",
	          "Chroma_Vector_1", "Chroma_Vector_2", "Chroma_Vector_3", "Chroma_Vector_4", "Chroma_Vector_5",
	          "Chroma_Vector_6", "Chroma_Vector_7", "Chroma_Vector_8", "Chroma_Vector_9", "Chroma_Vector_10",
	          "Chroma_Vector_11", "Chroma_Vector_12", "Chroma_Deviation")
	'''
	feature_names = ("Energy",)


	#arguments 2 and 3 are not in use
	#argument 7 and 8 store short term features and enable csv output respectively
	afe.mtFeatureExtractionToFile(filename,1,1,.05,.025,output_filename,True,True,False)

	#convert to json format
	csv_features = open(output_filename +'_st.csv','r')

	#add feature names as json keys
	json_features = []
	reader = csv.DictReader(csv_features,feature_names)
	#add rows to json string
	for row in reader:
		#json_features += json.dumps(row )
		#json_features += '\n'
		del row[None]
		json_features.append(row)

	csv_features.close()


	#remove unnecessary files
	os.remove(output_filename + ".csv")
	os.remove(output_filename + ".npy")
	os.remove(output_filename + "_st.csv")
	os.remove(output_filename + "_st.npy")



	#return the string of json formatted features
	return json.dumps(json_features)
