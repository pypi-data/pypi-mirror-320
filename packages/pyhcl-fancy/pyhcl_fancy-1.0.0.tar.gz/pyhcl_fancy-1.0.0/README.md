[![PyPI](https://img.shields.io/pypi/v/pyhcl-fancy.svg)](https://pypi.org/project/pyhcl-fancy/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyhcl-fancy.svg)](https://pypi.python.org/pypi/pyhcl-fancy)
[![License](https://img.shields.io/badge/license-apache-blue.svg)](https://raw.githubusercontent.com/ianms17/main/LICENSE)

# PyHCL Fancy
PyHCL Fancy is Python library that can be used to parse Terraform projects
written in HCL into a more developer-friendly tree structure.

## Documentation
We're on Read the Docs. Find more information at [https://readthedocs.org/projects/pyhcl-fancy/](https://readthedocs.org/projects/pyhcl-fancy/).

## Installation
This project is hosted on PyPI. It can be installed with the command below.
```
pip install pyhcl-fancy
```

## Usage
Once installed, a project can be parsed using the following.
```
from pyhcl_fancy.parser.parser import FancyParser

fancy_parser = FancyParser("path/to/terraform")
fancy_terraform.parse()
```