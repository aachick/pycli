[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# pycli

`pycli`, is a library for binding argument parsers and arbitrary classes to
reduce boilerplate code when writing CLI applications.

## Usage

The main `pycli` functionality is obtained with the `CliParser`
class. The main idea is to bind Python's standard `argparse.ArgumentParser`
class with the classes you define. This is to avoid having to write extra
boiler-plate code that parses CLI arguments, validates them in a certain
way, and passes them on to an object.

For parameter validation and typing to happen automatically, simply annotate
your class' constructor variables and add a docstring to it.

Consider the following setup:

```python
from typing import List

from pycli import CliParser


class MyClass:

    def __init__(self, a: str, b: int, c: List[int]):
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
```

The parser variable will act like a regular `argparse.ArgumentParser`
instance with the added benefit of having a `parse_args` method
that will return a `MyClass` object.

The following snippet illustrates what you might obtain when asking
for help (assume that the above snippet is in the example.py file):

```bash
$ python example.py --help
usage: example.py [-h] [--c [C ...]] a b

MyClass does a bunch of things and I would like to get instances of it from the CLI directly.

positional arguments:
  a            The a variable does this.
  b            [type: int] The b variable does that.

optional arguments:
  -h, --help   show this help message and exit
  --c [C ...]  [type: int] The c variable is a list of integers.
```

Notice that parameters with no default values are treated as positional arguments.

Running the program once more with actual arguments will produce the following:

```bash
$ python example.py foo 1
MyClass(a=foo, b=1, c=None)
```

Notice that the `c` parameter is a list of integers. To intialize the instance with
proper values, run like so:

```bash
$ python example.py foo 1 --c 1 2 3
MyClass(a=foo, b=1, c=[1, 2, 3])
```

The type hinting also enables for basic parameter validation. Trying to pass a non-int
value as an element of the `c` list will raise an error:

```bash
$ python examples/basic.py foo 1 --c 1 2 foo
usage: basic.py [-h] [--c [C ...]] a b
basic.py: error: argument --c: invalid int value: 'foo'
```

### Decorators

Going one step further, it is possible to simply decorate a method with the
`cli` decorator to define a command line entry point. Consider the following
example:

```python
from pycli import cli


@cli(MyClass)
def entry_point(my_obj: MyClass):
    print(my_obj)


entry_point()
```

In the example above, `my_obj` is the same as the `my_obj` object in
the example below:

```python
from pycli import CliParser

parser = CliParser(clz=MyClass)
my_obj = parser.parse_args()
print(my_obj)
```

By default, sys.argv is passed to the `entry_point` method. For testing
purposes, you can also pass a list of arguments or an `args` keyword
argument to `entry_point` like so:

```python
entry_point(["foo", "1", "--c", "1", "2", "3"])
```

Which is equivalent to:

```python
entry_point(args=["foo", "1", "--c", "1", "2", "3"])
```

Which is also equivalent to:

```bash
# With entry_point() in the script.
$ python example.py foo 1 --c 1 2 3
```

## Development

Development of the `pycli` library is welcome in the form of PRs, questions,
use cases to handle, or documentation improvements.

To get started with code contributions, first clone the project locally. Make sure
you have [poetry](https://github.com/python-poetry/poetry) installed as it is the
dependency management framework that it used.

At the project's root directory run the following to install the dev dependencies
and setup the project's pre-commit hooks:

```bash
poetry install --no-root
pre-commit install
```

Tests are performed using `pytest`. To run against your current Python version,
simply invoke `pytest`. To run against all supported Python versions, run `tox`.

## Testing

There are 3 levels of testing that are possible:

1. Testing the test suite with `make test` or `pytest`.
2. Testing the test suite and the examples `make test-all`
3. Testing with all supported python version `make test-tox` or `tox`.

## Roadmap

* [🚧] Manage cases where a class has multiple positional arguments that are sequences.
* [🚧] Manage errors caused by the `cli` decorator better.
