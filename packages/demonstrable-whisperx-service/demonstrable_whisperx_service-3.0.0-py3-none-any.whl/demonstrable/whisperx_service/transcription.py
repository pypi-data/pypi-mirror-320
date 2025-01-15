import gc
import logging
from datetime import timedelta
from pathlib import Path
import re
from typing import Iterable

from demonstrable.whisperx_service.exceptions import MissingAlignModelError

import srt
import torch
import whisperx
import whisperx.types

log = logging.getLogger(__name__)

DEFAULT_ASR_OPTIONS = {
    'suppress_numerals': True,
    'max_new_tokens': None,
    'clip_timestamps': None,
    'hallucination_silence_threshold': None,
}
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"


def precise_transcription(
    audio_file: Path,
    model_name="small",
    *,
    asr_options=None,
    device=None,
    compute_type=None,
    language=None,
    align_model_name=None,
) -> list[srt.Subtitle]:
    """Transcribe an audio file to text at word-level precision.

    Args:
        audio_file (Path): The path to the audio file to be transcribed.
        model_name (str, optional): The name of the whisper model to use for the transcription. Defaults to "small".
        asr_options (Mapping[str, any], optional): Overrides of default ASR options used when loading whisper's model.
            Defaults to None, meaning to use all of the defaults with the exception of `suppress_numerals` which we
            default to `True`. See `whisperx.load_model()` for more details.
        device (str, optional): The device to load the model on. Defaults to "cpu".
        compute_type (str, options): The compute type to use when loading the model. Defaults to "int8".
        language (str, optional): The language of the audio file. Defaults to auto-detection.
        align_model_name (str, optional): The name of the whisper model to use for alignment. Defaults to None, meaning
            to use the default alignment model (if any) for the language. If there is no default alignment model for
            the language, then an exception will be raised.

    Returns:
        list[srt.Subtitle]: _description_

    Raises:
        MissingAlignModelError: If a default alignment model is needed but is not available for the selected language.
    """
    model = load_model(model_name, device=device, compute_type=compute_type, language=language, asr_options=asr_options)
    result = model.transcribe(str(audio_file), language=language)

    # load alignment model and metadata
    try:
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], device=model.device, model_name=align_model_name
        )
    except ValueError as err:
        match = re.match("No default align-model for language: (.*)", str(err), re.IGNORECASE)
        if match is not None:
            raise MissingAlignModelError(language_code=match.group(1)) from err

        raise # pragma: no cover

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, str(audio_file), model.device)

    gc.collect()
    torch.cuda.empty_cache()

    return aligned_results_to_srt(result_aligned["word_segments"])


def load_model(model_name, *, device=None, compute_type=None, language=None, asr_options=None):
    asr_options = DEFAULT_ASR_OPTIONS | (asr_options or {})
    device = device or DEFAULT_DEVICE
    compute_type = compute_type or DEFAULT_COMPUTE_TYPE

    model = whisperx.load_model(
        model_name, device=device, compute_type=compute_type, language=language, asr_options=asr_options
    )
    return model


def aligned_results_to_srt(word_segments: Iterable[whisperx.types.SingleWordSegment]) -> list[srt.Subtitle]:
    srt_segments = []

    def add_srt(word, start, end):
        assert start < end
        srt_segments.append(
            srt.Subtitle(
                index=len(srt_segments) + 1,
                content=word,
                start=timedelta(seconds=start),
                end=timedelta(seconds=end),
            )
        )

    for segment in word_segments:
        # NB: We've seen segments with missing keys, so we skip segments which are missing required keys.
        required = {"word", "start", "end"}
        if missing := required.difference(segment.keys()):
            log.info("Skipping segment missing keys (%s): %s", ", ".join(missing), segment)
            continue

        add_srt(word=segment["word"], start=segment["start"], end=segment["end"])

    return srt_segments
