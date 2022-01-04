"""A simple example showing how you can bind a class to a
binded argument parser and use it from the command line.
"""
from typing import List

from pycli.parser import CliParser


class MyClass:
    def __init__(self, a: str, b: int, c: List[int] = None):
        """MyClass does a bunch of things and I would like to get
        instances of it from the CLI directly.

        Parameters
        ----------
        a
            The a variable does this.
        b
            The b variable does that.
        c
            The c variable is a list of integers.
        """
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return f"MyClass(a={self.a}, b={self.b}, c={self.c})"


parser = CliParser(clz=MyClass)
my_obj = parser.parse_args()
print(my_obj)
