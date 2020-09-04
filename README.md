# librtl

Python library for use in the route to live. This is a python repository which contains code for Route to Live. It has a docker artifact which can be used by Jenkins.

## Setting up Python3

1. brew install python3
2. python3 -m venv .venv
3. . .venv/bin/activate
4. python setup.py develop
5. pip install -r requirements-ci.txt

## Usage

This package installs a globally available tool called rtlctl. Use rtlctl --help to find usage information.
