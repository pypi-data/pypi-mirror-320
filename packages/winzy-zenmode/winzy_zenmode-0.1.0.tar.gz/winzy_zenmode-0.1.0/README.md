# winzy-zenmode

[![PyPI](https://img.shields.io/pypi/v/winzy-zenmode.svg)](https://pypi.org/project/winzy-zenmode/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy-zenmode?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy-zenmode/releases)
[![Tests](https://github.com/sukhbinder/winzy-zenmode/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy-zenmode/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy-zenmode/blob/main/LICENSE)

Zenmode stay focussed with only the priority windows and nothing else.

## Installation

First [install winzy](https://github.com/sukhbinder/winzy) by typing

```bash
pip install winzy
```

Then install this plugin in the same environment as your winzy application.
```bash
winzy install winzy-zenmode
```
## Usage

To get help type ``winzy  zenmode --help``

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd winzy-zenmode
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
