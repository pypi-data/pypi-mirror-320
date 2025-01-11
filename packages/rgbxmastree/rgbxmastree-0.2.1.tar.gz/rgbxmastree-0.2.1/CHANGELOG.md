# Changelog

## v0.2.0

- Remove Python version matrix from publish workflow.
- Remove lgpio and fix warnings being raised by tests.
- Add setuptools-scm and --version top level option.

## v0.1.0

- Updated project to use [uv](https://docs.astral.sh/uv/) for coordinating development.
- Extended RGBXmasTree class to distinguish between star LED and bauble LEDs.
- Added initial test suite including running via GitHub Actions.
- Created CLI using typer and added `color_shuffle` command.
- Updated docs to match the aforementioned code changes.
