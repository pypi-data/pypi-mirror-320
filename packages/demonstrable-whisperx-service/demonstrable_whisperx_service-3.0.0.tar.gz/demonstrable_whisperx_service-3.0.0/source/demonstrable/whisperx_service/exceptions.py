class TranscriptionError(Exception):
    "Base for all exceptions in demonstrable-transcription"
    pass


class ParseError(TranscriptionError):
    "An error occurred while parsing the script."
    pass


class UncollapsedSpaceError(ParseError):
    pass


class MarkerOutOfRangeError(ParseError):
    pass


class MarkerOutOfOrderError(ParseError):
    pass


class MissingAnchorError(TranscriptionError):
    """A relative marker has no corresponding anchor marker."""
    pass


class ZeroOffsetError(TranscriptionError):
    """A relative marker has an offset of 0."""
    pass


class RelativeMarkerResolutionError(TranscriptionError):
    "The resolved time for a relative marker is out of document order."
    pass


class MissingAlignModelError(TranscriptionError):
    "No align model was found for the given language."
    def __init__(self, language_code):
        self._language_code = language_code
        super().__init__(f"No align-model for language: {language_code}")

    @property
    def language_code(self):
        "The language code which is missing an alignment model."
        return self._language_code