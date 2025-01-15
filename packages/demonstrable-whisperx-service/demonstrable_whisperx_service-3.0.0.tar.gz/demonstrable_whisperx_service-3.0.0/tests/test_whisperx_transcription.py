from functools import reduce
from demonstrable.whisperx_service.transcription import precise_transcription, aligned_results_to_srt


def test_numbers_are_parsed_as_words(project_dirpath, tmp_path):
    wav_filepath = project_dirpath("audio-with-numbers") / "en" / "audio-with-numbers.wav"
    srts = precise_transcription(wav_filepath)
    actual = [sanitize(s.content.lower()) for s in srts]
    expected = [
        "one",
        "two",
        "monkey",
        "four",
        "forty-two",
    ]
    assert actual == expected


def test_spanish_numbers_are_parsed_as_words(project_dirpath, tmp_path):
    wav_filepath = project_dirpath("audio-with-numbers") / "es" / "audio-with-numbers.wav"
    srts = precise_transcription(wav_filepath, language="es")
    actual = [sanitize(s.content.lower()) for s in srts]
    expected = ["uno", "dos", "mono", "cuatro", "cuarenta", "y", "dos"]
    assert actual == expected


def test_aligned_results_to_srt_skips_segments_with_missing_required_keys():
    actual = aligned_results_to_srt(
        [
            {
                "word": "hello",
            }
        ]  # type: ignore
    )

    assert not actual


def sanitize(s: str):
    "Remove extra stuff from a string."
    return reduce(lambda accum, next: accum.replace(next, ""), [",", "."], s)
