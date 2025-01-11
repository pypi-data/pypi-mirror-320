import pytest

from rgbxmastree.commands.color_shuffle import run_session
from rgbxmastree.tree import RGBXmasTree

from unittest.mock import patch, Mock


@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def sample_tree():
    """Make an RGBXmasTree instance and turn it off at the end of every test"""
    tree = RGBXmasTree()
    yield tree
    tree.off()
    tree.close()


@pytest.mark.parametrize(
    "duration_hours",
    [1, 2, 0.5, 1.5],
    ids=["int_1", "int_2", "float_less_than_1", "float_greater_than_1"],
)
def test_session_duration(sample_tree, duration_hours):
    """Tests if the session duration is correctly calculated."""
    with patch(
        "rgbxmastree.commands.color_shuffle.sleep", return_value=None
    ) as mock_sleep:
        run_session(sample_tree, duration_hours, turn_off=False)
    # Extra initial sleep and extra final sleep
    expected_sleep_calls = len(sample_tree.baubles) + 2
    assert mock_sleep.call_count == expected_sleep_calls
    assert len(sample_tree.unlit) == 0


def test_bauble_colors(sample_tree):
    """Tests if baubles are assigned random colors."""
    with patch("rgbxmastree.commands.color_shuffle.sleep", return_value=None):
        run_session(sample_tree, 1, turn_off=False)

    assert all(bauble.color for bauble in sample_tree.baubles)


def test_turn_off_False(sample_tree):
    """Tests if the tree isn't turned off."""
    with patch("rgbxmastree.commands.color_shuffle.sleep", return_value=None):
        run_session(sample_tree, 1, False)

    assert len(sample_tree.unlit) == 0


def test_turn_off_True(sample_tree):
    """Tests if the tree is turned off by default."""
    with patch("rgbxmastree.commands.color_shuffle.sleep", return_value=None):
        run_session(sample_tree, 1)

    assert len(sample_tree.lit) == 0


@pytest.mark.parametrize("session_count", [1, 2])
def test_session_count(sample_tree, session_count):
    with patch(
        "rgbxmastree.commands.color_shuffle.sleep", return_value=None
    ) as mock_sleep:
        for count, session in enumerate(range(session_count), start=1):
            run_session(sample_tree, 0.5)
            assert len(sample_tree.lit) == 0
    # Calculate number of sleeps expected
    expected_sleep_calls = session_count * (len(sample_tree.baubles) + 2)
    assert mock_sleep.call_count == expected_sleep_calls
