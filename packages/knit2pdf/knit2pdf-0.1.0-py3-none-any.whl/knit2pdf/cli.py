from __future__ import unicode_literals
import click
from .knit2pdf import Knit2PDF
from .config.knit2pdfoptions import Knit2PDFOptions


@click.command()
@click.argument("youtube_link", required=True)
@click.option("--language", required=False, default="en", type=str, help="Language of the video to be transcribed.")
def cli(youtube_link: str, language: str) -> None:
    """
    Entrypoint for the CLI.

    Returns None
    """
    # Instantiate a Knit2PDF Client
    knit2pdf = Knit2PDF(youtube_link=youtube_link, video_language=language)
    knit2pdf.generate_pattern()


if __name__ == "__main__":
    cli()
