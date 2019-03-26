# A System for Collecting Background Audio Data for Parkinson's Research
## Senior Capstone Project
## Mason Flint, Benjamin Meyer, and Heather Graham

## Set-up
```
pip install pytest pyaudio numpy sklearn matplotlib eyed3 pydub hmmlearn gTTS
git clone https://github.com/grahamheather/pyAudioAnalysis.git
pip install -e pyAudioAnalysis
```

## For development
Run the following command from the root directory.
``` pip install -e . ```

## Testing
``` pytest ```

## Notes on changes from initial design
	* The design initially switched between recording, analyzing, and transmitting.  The implementation accomplishes recording concurrently with analyzing and transmitting to make use of the Raspberry Pi's multicore processors.
	* The design initially measured how close a new audio file matched a previous speaker by comparing the KL divergence of the estimated Gaussian distributions of each speaker.  However, the covariance matrices of the distributions are usually nonsingular making the divergence difficult to calculate.  As a simpler, more robust measure, the Euclidean distance between the mean of each cluster was chosen.  The use of K-Means to cluster slices of audio by speaker implies that speakers are expected to have approximately normal distributions with unit covariance, so this metric is suitable.  However, covariance matrices are still passed to the distance function for the ease of implementation of other measures in the feature.
	* The speaker diarization and re-identification module is not recommended due to unreliability of results. (It is disabled by default.)