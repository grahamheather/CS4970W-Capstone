import pytest

# supporting libraries
import pyaudio

# file under test
from CAT import record

# test opening stream
def test_open_stream():
	result = record.open_stream()
	assert type(result) == pyaudio.Stream
	

# test saving to file

# test saving a file if the disk is full

# test that feeding only silence will not save a file

# test that speech less than the min sample length will not save a file

# test that speech less than min sample length will not save a file but future speech will save a file

# test that speech between the min and max sample lengths saves a single file
# (check file length and contents)

# test that speech longer than the max sample length will save multiple files
# (check file length and contents)

# test that speech interspersed with silence saves appropriately

# test distinguishing speech from background noise

# test separating multiple voices from silence

# test separating multiple voices from background noise
