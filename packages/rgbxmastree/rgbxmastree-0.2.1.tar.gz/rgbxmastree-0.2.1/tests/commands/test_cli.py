import os
import subprocess
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("GPIOZERO_PIN_FACTORY") == "mock",
    reason="CLI test not compatible with environments that can't access GPIO pins.",
)


@pytest.mark.parametrize("subcommand", ["color-shuffle"])
def test_rgbxmastree_subcommand_in_help(subcommand, capfd):
    """
    Tests if running 'rgbxmastree --help' returns a valid help string including the specified subcommadn.
    """
    _ = subprocess.run(
        ["rgbxmastree", "--help"],
        text=True,
        check=True,
    )

    captured = capfd.readouterr()

    assert "Usage: rgbxmastree [OPTIONS] COMMAND" in captured.out
    assert subcommand in captured.out
    assert "--help" in captured.out


def test_rgbxmastree_color_shuffle_help(capfd):
    """
    Tests if running 'rgbxmastree color-shuffle --help' returns a valid help string.
    """
    _ = subprocess.run(
        ["rgbxmastree", "color-shuffle", "--help"],
        text=True,
        check=True,
    )

    captured = capfd.readouterr()

    assert "Usage: rgbxmastree color-shuffle" in captured.out
    assert "--duration" in captured.out
    assert "--sessions" in captured.out
    assert "--help" in captured.out
