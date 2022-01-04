"""Expose the main `CliParser` class that is the core of the pycli library."""
import argparse
import warnings

from enum import Enum
from inspect import Parameter, signature
from typing import Any, Dict, Generic, List, Optional, Sequence, Tuple, Type, TypeVar

from docstring_parser import parse
from typing_utils import issubtype


Cls = TypeVar("Cls")


def _generate_help(
    param_name: str,
    param_docs: Dict[str, str],
    param_type: Type = None,
    param_default: Any = None,
) -> str:
    help_msg = ""
    if param_type is not None:
        str_type = getattr(
            param_type, "__name__", str(param_type).replace("typing.", "")
        )
        help_msg += f"[type: {str_type}] "
        if hasattr(param_type, "__members__"):
            vals = _get_enum_choices(param_type)
            help_msg = (
                f"{help_msg[:-1]} | choices: {', '.join(str(val) for val in vals)}] "
            )
    help_msg += param_docs.get(param_name, "")
    if param_default:
        help_msg += f" (default: {param_default})"
    return help_msg.strip()


def _get_enum_choices(enum_obj: Enum) -> List[Any]:
    return [val.value for val in enum_obj.__members__.values()]


def _get_type(param: Parameter) -> Tuple[Optional[Type], bool]:
    """Return the underlying type and whether its a sequence or not."""
    param_type = param.annotation
    if param_type == param.empty:
        return None, False
    if isinstance(param_type, str):
        # ForwarRefs (identified as str values at runtime) are not well
        # supported. Therefore, we raise a UserWarning and consider the
        # type to be None.
        msg = (
            "ForwardRefs are not supported. Consider using"
            f" a regular type hint for {param.name}."
        )
        warnings.warn(msg, UserWarning)
        return None, False

    if issubtype(param_type, Sequence) and not isinstance(param_type, (bytes, str)):
        # If the type is a sequence (excluding str and bytes),
        # only consider the type of the first element.
        if hasattr(param_type, "__origin__"):
            return param_type.__args__[0], True
        # No explicit type so return None.
        return None, False
    return param_type, False


class CliParser(argparse.ArgumentParser, Generic[Cls]):
    """`CliParser` enables binding an arbitrary class to
    an ArgumentParser instance without having to re-declare all
    parameters inside the ArgumentParser.

    The basic mechanism of the `CliParser` is to parse
    the provided cls class object. Using its constrcutor, it will
    automatically set its command line arguments. Mandatory parameters
    of the constructor will be exposed as positional CLI arguments.
    Optional parameters of the constructor will be exposed as such.
    If optional parameters have defaults, such defaults will be used.

    The docstring of the constructor will be used in order to provide
    help messages. The docstring's description will be used as the
    CLI program's description. The `Parameters` section of the class'
    constructor's docstring will be used to provide help for each
    argument.

    If users choose to provide the constructor method with type hints,
    these will be used as the CLI argument's types.

    Attributes
    ----------
    clz : Type[Cls]
        An arbitrary class type to get an argument parser for.
    constructor : str
        The constructor method to use to obtain a new Cls instance.
        This defaults to '__init__'.
    mandatory_params : Dict[str, Type]
        The mandatory parameters' names mapped to their types. This
        is found from parsing the class' constructor method.
    optional_params : Dict[str, Tuple[Type, Any]]
        The optional parameters' names mapped to their types and
        default values. This is found from parsing the class'
        constructor method.

    Warnings
    --------
    If the provided class' constructor's annotations contain forward
    references, a UserWarning will be emitted. This is because the
    underlying type of a forward reference cannot be properly evaluated.

    Notes
    -----
    A known limitation of this system is the primitive handling of types
    declared within Sequences (other than str and bytes). In such cases,
    only the first type will be used. For example, the `Tuple[str, int]`
    annotation will result in the parser only considering the str type.

    Then again, (genuine question), how much complexity do you want to
    have when passing arguments through the command line?
    """

    def __init__(
        self, clz: Type[Cls], *args, constructor: str = "__init__", **kwargs
    ) -> None:
        self.clz = clz
        self.clz_name = clz.__qualname__

        target_func = getattr(self.clz, constructor)
        self.cls_constructor = target_func
        sig = signature(target_func)

        pos_only_params = []
        mandatory_params: Dict[str, Type] = {}
        optional_params: Dict[str, Tuple[Type, Any]] = {}
        param_values = dict(sig.parameters)
        param_values.pop("self", None)
        param_values.pop("cls", None)

        for param in param_values.values():
            is_pos = param.kind == param.POSITIONAL_ONLY
            is_varpos_req = (param.kind == param.POSITIONAL_OR_KEYWORD) and (
                param.default is param.empty
            )
            is_var_pos = (param.kind == param.KEYWORD_ONLY) and (
                param.default is param.empty
            )
            is_required = is_pos or is_varpos_req or is_var_pos

            (param_type, is_sequence) = _get_type(param)
            if is_pos:
                pos_only_params.append(param.name)

            if is_required:
                mandatory_params[param.name] = (param_type, is_sequence)
            else:
                # Only check for parameters with type annotations.
                optional_params[param.name] = (param_type, is_sequence, param.default)

        self.pos_only_params = pos_only_params
        self.mandatory_params = mandatory_params
        self.optional_params = optional_params

        cls_doc = parse(target_func.__doc__)

        description = cls_doc.short_description
        if description is None:
            description = ""
        if cls_doc.long_description:
            description += f"\n{cls_doc.long_description}"

        kwargs["description"] = description.strip()
        super().__init__(*args, **kwargs)

        doc_args = {arg.arg_name: arg.description for arg in cls_doc.params}
        for param, (param_type, _) in self.mandatory_params.items():
            arg_setup = {"help": _generate_help(param, doc_args, param_type=param_type)}
            if param_type is not None:
                arg_setup["type"] = param_type
            self.add_argument(param, **arg_setup)
        for (
            param,
            (param_type, is_sequence, param_default),
        ) in self.optional_params.items():
            help_msg = _generate_help(
                param, doc_args, param_type=param_type, param_default=param_default
            )
            arg_setup = {"dest": param, "required": False, "help": help_msg}

            if param_type is not None:
                arg_setup["type"] = param_type
                if is_sequence:
                    arg_setup["nargs"] = "*"
            if param_default is not None:
                arg_setup["default"] = param_default

            self.add_argument(f"--{param}", **arg_setup)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<{self.__class__.__qualname__}<->{self.clz.__qualname__}>"

    def parse_args(self, args: Sequence[str] = None) -> Cls:
        """Parse the command line and return a `Cls` instance based on
        the parsed values.

        Parameters
        ----------
        args : Sequence[str]
            The arguments to pass onto the parser to obtain a Cls
            instance. If unset, sys.argv will be used.

        Returns
        -------
        Cls
            An instance of the binded class.
        """
        ret_vals = super().parse_args(args=args)
        ret_dict = vars(ret_vals)
        if self.pos_only_params:
            args = [ret_dict.pop(arg) for arg in self.pos_only_params]
            if self.clz.__init__ == self.cls_constructor:
                return self.clz(*args, **ret_dict)
            return self.cls_constructor(*args, **ret_dict)

        if self.clz.__init__ == self.cls_constructor:
            return self.clz(**ret_dict)
        return self.cls_constructor(**ret_dict)
