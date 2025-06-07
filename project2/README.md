# android-package-analyzer

android-package-analyzer is a Python project to be used along with android-analyzer. android-analyzer was designed first to be used first to help with identifying and triaging packages of potential concern for follow-up analysis. This tool is designed to then be used to help with beginning analysis on a specific package that has been identified as suspicious.

## Installation

android-package-analyzer is written to be built as a Python wheel, which can be installed using pip. If installing from source code run `pip install` on the root directory of the project that contains the pyproject.toml file. If installing from the wheel file, run `pip install` on the wheel file.

## Dependencies

android-package-analyzer requires Python 3.6+, along with the following libraries:

    * hatchling
    * android-analyzer-common
    * pure-python-adb
    * requests

Additionally, in order to use android-package-analyzer, you need to have ADB installed on your computer and you need developer mode and debugging enabled on the Android device being analyzed.

## Running android-package-analyzer

To run android-package-analyzer, you can use `python -m android_package_analyzer [package_name]`. Along with the required `package_name` argument, android-package-analyzer has the below optional arguments:

    -d, --device DEVICE          The serial number of the Android device to be analyzed.
    -h, --help                   Display the help menu for android-package-analyzer.
    -k, --key-file               The path to a file containing a VirusTotal API key. Required when -s flag is used.
    -o, --outdir OUTPUT          Directory to output results to.
    -s, --scan                   A flag to have the tool submit the package to VirusTotal to be scanned for malware. The -k argument must be included when this argument is used.

## Future Work

This is an initial version of the tool, which can be further built up. Included are some ideas for further development of the tool:

    * Ensure the tool works with the formatting of ADB results for different versions of Android.
    * Integrate with an interactive dashboard: The interactive dashboard would leverage both this Python project, along with android-analyzer. The idea for that would be that the interactive dashboard would initially depict the results of android-analyzer, and the user would be able to use the dashboard to click on a package of interest, at which point the dashboard could use android-package-analyzer to begin providing information on that package.
    * Looking into the possibility of having the tool interact with APK decompiler tools.
    * Having the tool transfer the suspicious package to a testing environment where the package can be safely run with a packet sniffer running to begin dynamic analysis of the suspicious package.
