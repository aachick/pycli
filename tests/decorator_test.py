"""Test that the cli decorator can correctly be used."""
from pycli.decorators import cli

from .classes import Foo


def test_cli_with_class_only():
    """Test that decorating methods functions correctly."""

    @cli(Foo)
    def parse_obj(foo: Foo):
        assert foo.var1 == "foo"
        assert foo.var2 == 30

    parse_obj(["foo", "30"])
    parse_obj(args=["foo", "30"])
