import click
import srt


import demonstrable.whisperx_service.transcription
from demonstrable.whisperx_service.exceptions import MissingAlignModelError


@click.group()
def cli():
    pass


@cli.command()
def check():
    """Print the version of the whisperx-service."""
    click.echo("WhisperX Transcriber Ready")


@cli.command()
@click.argument("audio-file", type=click.Path(exists=True))
@click.argument("srt-file")
@click.option(
    "--model",
    default="small",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="""
The whisper model to use. A smaller model will be faster, use less RAM, and
take up less space on disk, but will produce lower quality transcriptions.

See https://github.com/openai/whisper#available-models-and-languages
for the list of available models.

Note that the first time you use a model it will be downloaded from the
internet, which may take some time with larger models.
""",
)
@click.option(
    "--device",
    default="cpu",
    type=click.Choice(["cpu", "cuda", "auto"]),
    help="""
The device for whisper to load the model on. Typically "cpu" (default) or "cuda" if that's available.
""",
)
@click.option(
    "--compute_type",
    default="int8",
    # See https://opennmt.net/CTranslate2/quantization.html#quantize-on-model-conversion
    type=click.Choice(
        [
            "int8",
            "int8_float32",
            "int8_float16",
            "int8_bfloat16",
            "int16",
            "float16",
            "bfloat16",
            "float32",
        ]
    ),
    help="The type to use for computation.",
)
@click.option(
    "--language",
    default=None,
    help="The language of the audio.",
)
@click.option(
    "--align-model",
    default=None,
    help="""The name of the alignment model.

    For example, NbAiLab/wav2vec2-xlsr-300m-norwegian for Norwegian. You can filter for "wav2vec2" and 
    "Automatic Speech Recognition" on Huggingface.com to find these models.""",
)
def transcribe(audio_file, srt_file, model, device, compute_type, language, align_model):
    """Transcribes [audio-file] to a word-level SRT file in [srt-file]."""
    try:
        transcription = demonstrable.whisperx_service.transcription.precise_transcription(
            audio_file,
            model_name=model,
            device=device,
            compute_type=compute_type,
            language=language,
            align_model_name=align_model,
        )

        with open(srt_file, "w") as o:
            o.write(srt.compose(transcription))

    except MissingAlignModelError as err:
        message = f"No default align-model for {err.language_code}. Try specifying --align-model."
        raise click.ClickException(message) from err


def main():
    return cli()  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover
    main()
