import random
import pytest
from rgbxmastree.tree import RGBXmasTree


@pytest.fixture
def make_tree():
    """Make an RGBXmasTree instance and turn it off at the end of every test"""
    tree = RGBXmasTree()
    yield tree
    tree.off()
    tree.close()


@pytest.fixture
def random_color():
    """Generate random rgb tuple."""
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b)


def test_RGBXmasTree__init__(make_tree):
    """Test the tree has an expected length of 25"""
    tree = make_tree
    assert len(tree) == 25


def test_RGBXmasTree_default_color(make_tree):
    tree = make_tree
    tree.on()
    assert [(1, 1, 1) for _ in tree] == [pixel.color for pixel in tree]


def test_RGBXmasTree_all_same_color(make_tree, random_color):
    """Test setting the same color for each light in a tree"""
    tree = make_tree
    assert tree.color == (0, 0, 0)
    color_to_set = random_color
    for pixel in tree:
        pixel.color = color_to_set
    assert tree.color == color_to_set


def test_RGBXmasTree_different_colors(make_tree, random_color):
    """Test setting different colors for each pixel in a tree"""
    tree = make_tree
    assert tree.color == (0, 0, 0)
    colors_set = []
    for pixel in tree:
        color_to_set = random_color
        pixel.color = color_to_set
        colors_set.append(color_to_set)
    assert colors_set == [pixel.color for pixel in tree]


def test_RGBXmasTree_unlit_by_default(make_tree):
    """Test no pixels are off when a RGBXmasTree is instantiated"""
    tree = make_tree
    assert len(tree.lit) == 0
    assert len(tree.unlit) == len(tree)


def test_RGBXmasTree_all_lit(make_tree):
    """Test all pixels can be switched on"""
    tree = make_tree
    tree.on()
    assert len(tree.lit) == len(tree)
    assert len(tree.unlit) == 0


def test_RGBXmasTree_all_lit_then_unlit(make_tree):
    """Test all pixels can be switched off"""
    tree = make_tree
    tree.on()
    assert len(tree.lit) == len(tree)
    assert len(tree.unlit) == 0
    tree.off()
    assert len(tree.lit) == 0
    assert len(tree.unlit) == len(tree)


def test_RGBXmasTree_star_only(make_tree):
    """Tests that the star can be switched on/off independently of the baubles"""
    tree = make_tree
    tree.star.on()
    assert tree.star in tree.lit
    assert len(tree.lit) == 1
    assert tree.star not in tree.unlit
    assert len(tree.unlit) == (len(tree) - 1)


def test_RGBXmasTree_baubles_only(make_tree):
    """Test that the baubles can be switched on/off independently of the star"""
    tree = make_tree
    for bauble in tree.baubles:
        bauble.on()
    assert tree.star not in tree.lit
    assert len(tree.baubles) == len(tree.lit)


def test_RGBXmasTree_star_and_baubles(make_tree):
    """Test that star and baubles can be switched on/off together"""
    tree = make_tree
    assert tree.star not in tree.baubles
    assert len(tree.baubles) == (len(tree) - 1)
    tree.star.on()
    assert set(tree.baubles) == set(tree.unlit)
    tree.star.off()
    for bauble in tree.baubles:
        bauble.on()
    assert tree.star not in tree.lit
