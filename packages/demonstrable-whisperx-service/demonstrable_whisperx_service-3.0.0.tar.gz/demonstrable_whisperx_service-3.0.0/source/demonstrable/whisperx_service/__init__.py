from collections import namedtuple

Version = namedtuple("Version", ["major", "minor", "patch"])

__version__ = "3.0.0"
__version_info__ = Version(*(__version__.split(".")))
__name__ = "transcription_whisperx_service"

