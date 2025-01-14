from .model import ASRAudio

DEFAULT_ASR_AUDIO = ASRAudio(format="pcm", sample_rate=1600, codec="raw", channel=1)
