"""Simple test configuration for application."""
from enum import Enum
from typing import List


class FooEnum(Enum):

    A = "choice1"
    B = "choice2"


class Foo:
    def __init__(
        self, var1: str, var2: int, enum1: FooEnum = FooEnum.A, list1: List[int] = None
    ) -> None:
        """The Foo class does many very useful things.

        Parameters
        ----------
        var1
            var1 description.
        var2
            var2 description.
        enum1
            enum1 description.
        list1
            list1 description.
        """
        self.var1 = var1
        self.var2 = var2
        self.enum1 = enum1
        self.list1 = list1

    @classmethod
    def from_cli(
        cls, var1: str, var2: int, enum1: FooEnum = FooEnum.B, list1: List[int] = None
    ) -> "Foo":
        """Obtain a Foo instance by passing arguments from the CLI.
        Different default values apply.

        Parameters
        ----------
        var1
            var1 description.
        var2
            var2 description.
        enum1
            enum1 description.
        list1
            list1 description.
        """
        return cls(var1, var2, enum1=enum1, list1=list1)
