from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("rgbxmastree")
except PackageNotFoundError:
    # package is not installed
    pass
