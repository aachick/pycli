"""Test that the CliParser class functions correctly in as
many situations as possible.
"""
import sys

from typing import List

import pytest

from _pytest.capture import CaptureFixture

from pycli import CliParser

from .classes import Foo, FooEnum


@pytest.mark.parametrize(
    "constructor,enum_value", [("__init__", FooEnum.A), ("from_cli", FooEnum.B)]
)
def test_binded_arg_parser_return_val(constructor: str, enum_value: FooEnum):
    """Test that the binded argument parser works as expected in an
    ideal situation by returning the correct type and an instance with
    expected values.
    """
    parser = CliParser(clz=Foo, constructor=constructor)
    assert "var1" in parser.mandatory_params
    assert "var2" in parser.mandatory_params
    assert "enum1" in parser.optional_params
    assert "list1" in parser.optional_params

    cli_args = ["my string", "5", "--list1", "30", "15"]

    foo = parser.parse_args(cli_args)
    assert isinstance(foo, Foo)

    assert foo.var1 == "my string"
    assert foo.var2 == 5
    assert foo.enum1 == enum_value
    assert foo.list1 == [30, 15]

@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires python3.8 or higher.")
# @pytest.mark.xfail(sys.version_info < (3, 8), reason="Requires python3.8 or higher.")
@pytest.mark.parametrize(
    "cli_args,constructor,expected",
    [(["1"], "__init__", 1), (["2", "--b", "30"], "from_cli", 60)],
)
def test_binded_arg_parser_with_positional_only(
    cli_args: list, constructor: str, expected: int
):
    """Test that binding an argument parser to a class with positional
    only arguments works as expected. Positional only parameters are
    supported from version 3.8 onwards only.
    """
    foo2_str = """\
class Foo2:
    def __init__(self, a: int, /) -> None:
        self.a = a

    @classmethod
    def from_cli(cls, a: int, /, b: int = 20):
        return cls(a * b)
    """
    # This is a very ugly workaround to the tox/pytest combination
    # not caring that this test is skipped under 3.7. Load the class
    # via a string so that the syntax error can be caught.
    glob = {}
    try:
        exec(foo2_str, glob)
        Foo2 = glob["Foo2"]
    except SyntaxError:
        # For some reason tox doesn't care that this is skipped
        # for versions under 3.8
        Foo2 = object

    parser = CliParser(clz=Foo2, constructor=constructor)
    assert "a" in parser.pos_only_params

    foo2 = parser.parse_args(cli_args)
    assert isinstance(foo2, Foo2)
    assert foo2.a == expected


@pytest.mark.parametrize(
    "cli_args",
    [
        [],
        ["foo", "bar"],
        ["my string", "10", "--enum1", "not_a_val"],
        ["my string", "10", "--list1", "not_an_int"],
    ],
)
def test_binded_arg_parser_with_invalid_values(
    cli_args: List[str], capsys: CaptureFixture
):
    """Test that validation of arguments will occur by relying on
    type hints. All the cli_args contain invalid constructor arguments.
    """
    parser = CliParser(clz=Foo)
    with pytest.raises(SystemExit):
        parser.parse_args(cli_args)
        out_err = capsys.readouterr()
        assert out_err.err


def test_str_and_repr():
    """Test that the srt and repr methods are equal and provide
    a helpful view of what's going on.
    """
    parser = CliParser(clz=Foo)
    parser_repr = repr(parser)
    parser_str = str(parser)

    assert parser_repr == parser_str == "<CliParser<->Foo>"


def test_help_message(capsys: CaptureFixture):
    """Test that the help message provides useful and expected information."""
    parser = CliParser(clz=Foo)
    parser.print_help()

    out_err = capsys.readouterr()
    out = out_err.out
    assert out
    attrs = ["var1", "var2", "enum1", "list1"]
    for attr in attrs:
        assert attr in out
