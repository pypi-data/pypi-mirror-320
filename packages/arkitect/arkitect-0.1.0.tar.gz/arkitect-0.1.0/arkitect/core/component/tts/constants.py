# Message version and header size
PROTOCAL_VERSION = 0b1
HEADER_SIZE = 0b1

# Message Type:
INVALID = 0b0000
FULL_CLIENT = 0b0001
AUDIO_ONLY_CLIENT = 0b0010
FULL_SERVER = 0b0011
AUDIO_ONLY_SERVER = 0b0100
FRONT_END_RESULT_SERVER = 0b0101
ERROR = 0b0110
SERVER_ACK = AUDIO_ONLY_SERVER

# Message Type Specific Flags
NO_SEQUENCE = 0b0000  # no check sequence
POS_SEQUENCE = 0b0001
LAST_NO_SEQUENCE = 0b0010
NEG_SEQUENCE = 0b0011
WITH_EVENT = 0b0100


# Message Serialization
NO_SERIALIZATION = 0b0000
JSON = 0b0001

# Message Compression
NO_COMPRESSION = 0b0000
GZIP = 0b0001


# 默认事件,对于使用事件的方案，可以通过非0值来校验事件的合法性
EventNone = 0


EventStartConnection = 1
EventFinishConnection = 2


EventConnectionStarted = 50
EventConnectionFailed = 51
EventConnectionFinished = 52


EventStartSession = 100
EventFinishSession = 102

EventSessionStarted = 150
EventSessionFinished = 152
EventSessionFailed = 153

EventTaskRequest = 200

EventTTSSentenceStart = 350
EventTTSSentenceEnd = 351
EventTTSResponse = 352


NAMESPACE = "BidirectionalTTS"
INT_SIZE = 4
DEFAULT_SPEAKER = "zh_female_tianmeixiaoyuan_moon_bigtts"
