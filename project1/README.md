# android-analyzer

android-analyzer is a Python library to help with viewing processes and packages on an Android device to help with identifying packages that are using more data than they should or are displaying unusual or suspicious behavior.

## Installation

android-analyzer is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

android-analyzer requires Python 3.6+, along with the following libraries:

    * hatchling
    * psutil
    * pure-python-adb

## Running android-analyzer

To run android-analyzer, you can use `python -m android_analyzer`. android-analyzer has no required arguments, but it does include optional arguments listed below.

    -a, --analyzers ANALYZERS    A comma delimited list of which analytics to run. Current values: appnetstats, processes
    -d, --device DEVICE          The serial number of the Android device to be analyzed
    -h, --help                   Display the help menu for android-analyzer
    -o, --outdir OUTPUT          Directory to output results to

## Future Work

This is an initial version of the tool, which can be further built up. Included are some ideas for further development of the tool:

    1. Add an interactive dashboard: This could help to improve visualization and cause anomalies in the data to better stand out. Further, it could help to enable the ability to point and click on an anomalous entry to enable follow-on analysis of a specific package.
    1. Follow-on analytics for individual packages: If anomalous behavior is seen with a specific process or package, follow-on analytics could be used to further investigate the suspicious process/package. This could include things like looking for associated logcat logs or analyzing package manifests.
    1. Looking into the possibility of having the tool interact with APK decompiler tools.
