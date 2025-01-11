import logging
import random
import typer
from time import sleep
from typing_extensions import Annotated
from rgbxmastree.tree import RGBXmasTree


logger = logging.getLogger("RGBXmasTree: Color Shuffle")


def run_session(tree, duration_hours, turn_off=True):
    """Run a lighting session.

    Args:
        tree: RGBXmasTree instance.
        duration_hours float: Length of the session to run in hours.
        turn_off bool: Turn off tree at end of the session. Default: True

    """
    duration_seconds = duration_hours * 60 * 60
    interval_count = len(tree.baubles) + 1
    interval_seconds = duration_seconds / interval_count
    logger.debug(
        f"Starting session of {interval_count} intervals"
        f" of {interval_seconds / 60:.2f} minutes."
    )
    sleep(interval_seconds)
    while tree.unlit:
        bauble = random.choice(tree.unlit)
        colour = random.choice(["red", "green", "blue", "yellow"])
        logger.debug(f"Setting bauble {bauble.index} to {colour}.")
        bauble.color = colour
        sleep(interval_seconds)
    if turn_off:
        tree.off()


def _configure_logging(level):
    """Bundle up logging config code.

    Args:
        level: Logging level, string or int as per python
            conventions.

    """
    handler = logging.StreamHandler()
    logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=logging_format, handlers=[handler])


app = typer.Typer()


@app.command()
def color_shuffle(
    duration: Annotated[
        float,
        typer.Option(
            "--duration",
            "-d",
            help="Duration of a session of lighting up the tree in hours.",
        ),
    ] = 1.0,
    sessions: Annotated[
        int,
        typer.Option("--sessions", "-s", help="Number of sessions of tree lighting."),
    ] = 1,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity level (can be specified multiple times).",
        ),
    ] = 0,
):
    """Shuffle the colors of the Christmas tree lights."""
    # Determine the logging level based on the number of --verbose options
    logging_level = logging.WARNING - (verbose * 10)
    _configure_logging(logging_level)
    logger.info(f"Running {sessions} sessions of {duration} hours each.")
    try:
        tree = RGBXmasTree(brightness=0.05)
        tree.star.color = "gold"
        for count, session in enumerate(range(sessions), start=1):
            logging.debug(f"Starting session {count} of {sessions}.")
            run_session(tree, duration)
            logging.debug(f"Session {count} finished.")
    finally:
        tree.off()
