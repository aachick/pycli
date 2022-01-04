"""pycli is a library that enables users to bind arbitrary classes
with a CLI argument parser to reduce boilerplate code.
"""
__all__ = ["CliParser", "cli"]
__version__ = "0.1.0"

from pycli.decorators import cli
from pycli.parser import CliParser
