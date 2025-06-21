# android-dashboard

android-dashboard is a Python dashboard used to display results from android-analyzer, which is designed to help with viewing packages on an Android device that are using large amounts of data and showing potentially suspicious behavior.

Android devices have often been victim to packages that have too much privilege and collect more data than they should and to malicious packages disguised as a game or useful app. With Android devices, ADB provides a significant amount of data that could help to identify suspicious packages, but the data could exist across various commands, which may not be well-known. This tool was designed to leverage pure-python-adb to run multiple ADB commands and combining the results and providing them in an easy to use dashboard for follow-on analysis.

## Installation

android-dashboard is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

android-dashboard requires Python 3.6+, along with the following libraries:

    * hatchling
    * android-analyzer-common
    * android-analyzer
    * android-package-analyzer
    * dash
    * pandas
    * pure-python-adb

Additionally, in order to use android-dashboard, you need to have ADB installed on your computer and you need developer mode and debugging enabled on the Android device being analyzed.

## Running android-dashboard

To run android-dashboard, you can use `python -m android_dashboard`. android-dashboard takes no arguments. Once it is running, you can connect to the dashboard using a browser.

## Future Work

This is an initial version of the tool, which can be further built up. Included are some ideas for further development of the tool:

    * Make the charts clickable, and then have them run analysis on the package that was clicked, which shows up in another tab or another section of the dashboard.
    * Allow for customization of the charts displayed.
    * Improve the look and feel of the dashboard.
    * Add dark mode.
