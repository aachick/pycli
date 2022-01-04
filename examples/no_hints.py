"""A simple example showing that even without type hints and a
method docstring, the binded argument parser still works. However,
the help/usage messages won't be quite as nice.
"""
from pycli import CliParser


class MyClass:
    def __init__(self, a, b, c=None):
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return f"MyClass(a={self.a}, b={self.b}, c={self.c})"


parser = CliParser(clz=MyClass)
my_obj = parser.parse_args()
print(my_obj)
