# android-analyzer

android-analyzer is a Python library to help with viewing processes and packageson an Android device to help with identifying packages that are using more data than they should or are displaying unusual or suspicious behavior.

## Installation

android-analyzer is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

android-analyzer requires Python 3.6+, along with the following libraries:

    * psutil
    * pure-python-adb

## Running android-analyzer

To run android-analyzer, you can use `python -m android_analyzer`
