import sys
from typing import Optional
from gpiozero.exc import NativePinFactoryFallback, PinFactoryFallback
from typing_extensions import Annotated
import typer

from .commands.color_shuffle import app as color_shuffle_app


# Setup warning filtering
if not sys.warnoptions:
    import warnings

    warnings.filterwarnings("ignore", category=PinFactoryFallback)
    warnings.filterwarnings("ignore", category=NativePinFactoryFallback)


app = typer.Typer()


def _version_callback(version):
    if version:
        from rgbxmastree import __version__

        print(f"rgbxmastree version: {__version__}")
        raise typer.Exit()


@app.callback()
def version(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", callback=_version_callback, help="Show version and exit."
        ),
    ] = None,
):
    pass


app.add_typer(color_shuffle_app)
