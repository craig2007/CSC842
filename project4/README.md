# logcat-analyzer

logcat-analyzer is a tool to help analyze logcat logs and identify the most critical logs. The tool pulls the last 24 hours worth of logcat logs from a selected device. It then sends the logs to the LLaMA AI model to provide each log entry a synopsis of the entry, score regarding how critical the log entry is, and a reason for the score.

## Installation

logcat-analyzer is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

logcat-analyzer requires Python 3.6+, along with the following libraries:

    * hatchling
    * android-analyzer-common
    * pure-python-adb
    * requests

Additionally, in order to use logcat-analyzer, you need to have ADB and ollama installed on your computer and you need developer mode and debugging enabled on the Android device being analyzed.

## Running android-package-analyzer

To run android-package-analyzer, you can use `python -m android_package_analyzer [package_name]`. Along with the required `package_name` argument, android-package-analyzer has the below optional arguments:

    -d, --device DEVICE          The serial number of the Android device to be analyzed.
    -h, --help                   Display the help menu for android-package-analyzer.
    -o, --outdir OUTPUT          Directory to output results to.

## Future Work

This is an initial version of the tool, which can be further built up. Included are some ideas for further development of the tool:

    * Ensure the tool works with the formatting of ADB results for different versions of Android.
    * Continue adjusting the prompt to improve upon the scoring of the criticality of each log entry.
    * Enable the AI model to be run remotely on a device that is better for running AI models.
