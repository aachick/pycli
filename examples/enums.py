"""A simple example showing how you can use enum values when
binding a class to a binded argument parser and use it from
the command line. The --help message will show you both the
possible enum values.
"""
from enum import Enum
from typing import List

from pycli import CliParser


class Foo(Enum):

    A = "foo"
    B = "bar"



class MyClass:
    def __init__(self, a: Foo, b: int, c: List[int] = None):
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
