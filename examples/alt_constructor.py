"""A simple example showing how you can use a method other
than the class' __init__ method to obtain an object instance.
"""
from typing import List

from pycli import CliParser


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

    @classmethod
    def from_cli(cls, a: str):
        """Obtain a MyClass instance through an alternative method.

        Parameters
        ----------
        a
            The a variable that does stuff.
        """
        return cls(a, 42, c=["20", "30"])


parser = CliParser(clz=MyClass, constructor="from_cli")
my_obj = parser.parse_args()
print(my_obj)
