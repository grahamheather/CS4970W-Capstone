import pyaudio

# universal constants
MILLISECONDS_PER_SECOND = 1000

# hardware specs
NUM_CORES = 4

# audio storage settings
MIN_EMPTY_SPACE_IN_BYTES = 7064096

# audio recording settings
VAD_LEVEL = 2 # "integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive." -py-webrtcvad docs
FORMAT = pyaudio.paInt16 # WebRTC VAD only accepts 16-bit audio
NUM_BYTES = 2 # 16 bits in format = 2 bytes in format
NUM_CHANNELS = 1 # WebRTC VAD only accepts mono audio
RATE = 48000 # WebRTC VAD only accepts 8000, 16000, 32000 or 48000 Hz
VAD_FRAME_MS = 30 # WebRTC VAD only accepts frames of 10, 20, or 30 ms
VAD_FRAME_SIZE = int(RATE * VAD_FRAME_MS / MILLISECONDS_PER_SECOND)
VAD_FRAME_BYTES = VAD_FRAME_SIZE * NUM_BYTES * NUM_CHANNELS

# settings based on system timing and situation
PERIODIC_SAMPLE_RATE = .5  # how often to check when no speech has been detected, in seconds
MIN_SAMPLE_LENGTH = .75 # smallest sample to save, in seconds
MAX_SAMPLE_LENGTH = 30 # largest sample to save (larger ones will be split), in seconds
MAX_SILENCE_LENGTH = .5 # largest length of silence to include in a single sample

# calculated from system settings
PERIODIC_SAMPLE_FRAMES = int(PERIODIC_SAMPLE_RATE * MILLISECONDS_PER_SECOND / VAD_FRAME_MS)
MIN_SAMPLE_FRAMES = int(MIN_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / VAD_FRAME_MS)
MAX_SAMPLE_FRAMES = int(MAX_SAMPLE_LENGTH * MILLISECONDS_PER_SECOND / VAD_FRAME_MS)
MAX_SILENCE_FRAMES = int(MAX_SILENCE_LENGTH * MILLISECONDS_PER_SECOND / VAD_FRAME_MS)

# speaker diarization settings
SPEAKER_DIARIZATION = False
MAX_SPEAKERS = 2

# speaker re-identification settings
SPEAKER_REID_DISTANCE_THRESHOLD = 3