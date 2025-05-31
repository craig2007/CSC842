# android-analyzer-common

android-analyzer-common is not meant to be a standalone package. It is designed to be a Python wheel containing common code used across different tools in the android-analyzer toolset.

## Installation

android-analyzer-common is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

android-analyzer-common requires Python 3.6+, along with the following libraries:

    * hatchling
    * pure-python-adb

## Running android-analyzer-common

This wheel is not meant to be a standalone tool that is run directly. It is meant to provide common functions used by other android-analyzer tools.
