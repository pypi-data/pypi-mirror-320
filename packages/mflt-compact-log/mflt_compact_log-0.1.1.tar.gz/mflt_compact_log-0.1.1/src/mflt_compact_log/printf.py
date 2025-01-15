"""
Recreate C's printf function in pure Python.

References:

- https://en.wikipedia.org/wiki/Printf#Syntax
- https://cplusplus.com/reference/cstdio/printf/

Tools:

- https://openrepl.com/
"""

from __future__ import annotations

import dataclasses
import logging
import struct
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Literal, Union, cast

import pyparsing as pyp
from typing_extensions import NotRequired, Protocol, TypedDict, assert_never

_LOG = logging.getLogger(__name__)


Placeholder = Literal["*"]
PLACEHOLDER: Placeholder = "*"
"""
printf format specifiers can contain a '*' character to indicate that an
argument should be used to determine the width or precision. When parsing
the format string, we represent this with the PLACEHOLDER constant, but
when rendering the format string, we replace it with the actual value.
"""

MAX_WIDTH = 128
"""
The maximum width that we will allow for a conversion specifier. This is
to prevent the format string from being used to consume excessive memory.
"""


@dataclasses.dataclass(frozen=True, kw_only=True)
class TextPart:
    """A part of the format string that is not a conversion specifier."""

    raw: str = dataclasses.field(repr=False)

    def __str__(self) -> str:
        return self.raw


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpecifierPart:
    """A part of the format string that is a conversion specifier."""

    raw: str = dataclasses.field(repr=False)
    conversion_specifier: str
    flags: str
    width: int | Placeholder | None
    precision: int | Placeholder | None
    length_modifier: str

    def __post_init__(self) -> None:
        for attr in ("width", "precision"):
            value = getattr(self, attr)

            if value is None:
                continue
            elif value == PLACEHOLDER:
                continue

            assert isinstance(value, int)

            if attr == "precision":
                if value < 0:
                    # The C standard says that if the precision is negative,
                    # it should be treated as if it were omitted.
                    _LOG.warning("%r is negative; ignoring precision: %s", attr, value)
                    value = None
            elif attr == "width":
                if value < 0:
                    # The C standard says that if the width is negative,
                    # the flag '-' is added and the width is made positive.
                    value = abs(value)

                    if "-" not in self.flags:
                        object.__setattr__(self, "flags", "-" + self.flags)

            if value and value > MAX_WIDTH:
                _LOG.warning("%r is too large: %s", attr, value)
                value = MAX_WIDTH

            object.__setattr__(self, attr, value)

    def __str__(self) -> str:
        return self.raw


class ResolvedSpecifierPart(SpecifierPart):
    """
    A specifier part with resolved (non-placeholder) width and precision values.
    """

    width: int | None
    precision: int | None


Part = Union[TextPart, SpecifierPart]


def make_parser() -> pyp.ParserElement:
    percent_sign = pyp.Suppress("%")
    flags = pyp.Optional(pyp.Word(" -+0#").leaveWhitespace())("flags")
    width = pyp.Optional(
        pyp.Or([
            pyp.Literal("*"),
            pyp.Word(pyp.nums),
        ])
    )("width")
    precision = pyp.Optional(
        pyp.Suppress(".")
        + pyp.Or([
            pyp.Literal("*"),
            pyp.Word(pyp.nums),
            pyp.Empty(),
        ])
    )("precision")
    length_modifier = pyp.Optional(pyp.oneOf("hh h l ll j z t L"))("length_modifier")
    conversion_specifier = pyp.oneOf("b B d i u o x X f F e E g G a A c s p n %")(
        "conversion_specifier"
    )
    rv = percent_sign + pyp.Or([
        pyp.Literal("%"),
        flags + width + precision + length_modifier + conversion_specifier,
    ])
    return rv.parseWithTabs()


PARSER = make_parser()


class ParseResults(TypedDict):
    flags: NotRequired[str]
    width: NotRequired[str]
    precision: NotRequired[tuple[str] | tuple[()]]
    length_modifier: NotRequired[str]
    conversion_specifier: str


RawArg = Union[str, float, int]
"""The arguments that we support for printf format specifiers."""

_INVALID_POINTER_INT = 0
"""Value to return when we couldn't interpret an integer argument."""


def _ensure_int(arg: RawArg) -> int:
    if isinstance(arg, int):
        return arg

    _LOG.warning("Invalid integer argument: %s", type(arg))

    # If we got a float, bitcast it to an integer
    if isinstance(arg, float):
        packed = struct.pack(">f", arg)
        return struct.unpack(">I", packed)[0]

    return _INVALID_POINTER_INT


def _sign(value: float, *, flags: str) -> str:
    if value < 0:
        return "-"
    elif "+" in flags:
        return "+"
    elif " " in flags:
        return " "
    else:
        return ""


_SIZES: Mapping[str, int] = {
    "": 4,
    "hh": 1,
    "h": 2,
    "l": 4,
    "ll": 8,
    # To format the following types correctly, we would need
    # to know the size of the type on the target platform, but
    # we don't have that information.
    "j": 4,
    "z": 4,
    "t": 4,
}
"""
The mapping of length modifiers to struct pack format strings
which will help us determine the size of the integer argument
so that we can resize it to fit the format specifier.

https://docs.python.org/3/library/struct.html#format-characters
"""


def _resize_integer(value: int, *, size: int, signed: bool) -> int:
    assert 1 <= size <= 16

    max_unsigned_value = 1 << (8 * size)
    value %= max_unsigned_value

    if signed and value & (1 << (8 * size - 1)):
        value -= max_unsigned_value

    return value


def _render_integer(part: ResolvedSpecifierPart, arg: RawArg) -> str:
    value = _ensure_int(arg)

    # A special case for the ' ' flag: if the value is zero and the precision is zero, the result is an empty string
    if not value and not part.precision and " " in part.flags:
        return " "

    sign = ""
    signed = part.conversion_specifier not in {"u", "o", "x", "X", "b", "B", "p"}
    if signed:
        sign = _sign(value, flags=part.flags)

    if not (size := _SIZES.get(part.length_modifier)):
        _LOG.warning("Invalid length modifier: %r", part.length_modifier)
        return part.raw

    value = _resize_integer(value, size=size, signed=signed)

    # Translate some conversion specifiers to Python format specifiers
    format_spec = {
        "i": "d",
        "u": "d",
        "B": "b",
        "p": "x",  # For pointers, use hexadecimal
    }.get(part.conversion_specifier, part.conversion_specifier)

    formatted = format(abs(value), format_spec)

    # Special case for zero precision: if the value is zero, the result is an empty string
    if not value and part.precision == 0:
        formatted = ""

    # Support "alternative form" for octal and hexadecimal numbers and pointers
    prefix = ""
    if part.conversion_specifier == "p" and value:
        prefix = "0x"
    # NB: prefix is only added for non-zero values
    elif "#" in part.flags and value:
        prefix = {
            "o": "0",
            "x": "0x",
            "X": "0X",
            "b": "0b",
            "B": "0B",
        }.get(part.conversion_specifier, "")

    # apply zero padding
    if not formatted:
        pass
    elif part.precision:
        formatted = formatted.rjust(int(part.precision), "0")
    elif part.width and "0" in part.flags and "-" not in part.flags:
        formatted = formatted.rjust(int(part.width) - len(prefix) - len(sign), "0")

    formatted = sign + prefix + formatted

    # apply space padding
    if not part.width:
        pass
    elif "-" in part.flags:
        formatted = formatted.ljust(int(part.width))
    else:
        formatted = formatted.rjust(int(part.width))

    return formatted


_INVALID_POINTER_FLOAT = 0.0
"""Value to return when we couldn't interpret a float argument."""


def _ensure_float(arg: RawArg) -> float:
    if isinstance(arg, float):
        return arg

    _LOG.warning("Invalid float argument: %s", type(arg))

    # If we got an integer, bitcast it to a float
    if isinstance(arg, int):
        packed = struct.pack(">I", arg)
        return struct.unpack(">f", packed)[0]

    return _INVALID_POINTER_FLOAT


def _render_float(part: ResolvedSpecifierPart, arg: RawArg) -> str:
    arg = _ensure_float(arg)

    format_str = "{:"

    if "-" in part.flags:
        format_str += "<"

    for flag in part.flags:
        if flag in "+0":
            format_str += flag

    if part.width:
        format_str += str(part.width)

    if part.precision is not None:
        format_str += "." + str(part.precision)

    format_str += part.conversion_specifier
    format_str += "}"

    return format_str.format(arg)


_NULL_POINTER_STRING = "(null)"
_INVALID_POINTER_STRING = "(???)"


def _ensure_string(arg: RawArg) -> str:
    if isinstance(arg, str):
        return arg

    # If we didn't get a string, we would have to interpret
    # the argument as a pointer to a string. There's a special
    # case for NULL pointers, which should be rendered as "(null)".
    if isinstance(arg, int) and arg == 0:
        return _NULL_POINTER_STRING

    # Otherwise, we can't do anything useful with the argument,
    # as we don't have access to the memory where the string was.
    _LOG.warning("Invalid string argument: %s", type(arg))

    return _INVALID_POINTER_STRING


def _render_string(part: ResolvedSpecifierPart, arg: RawArg) -> str:
    arg = _ensure_string(arg)

    format_str = "{:"
    format_str += "<" if "-" in part.flags else ">"

    if part.width:
        format_str += str(part.width)

    if part.precision is not None:
        format_str += "." + str(part.precision)

    format_str += "s}"

    return format_str.format(arg)


def _render_char(part: ResolvedSpecifierPart, arg: RawArg) -> str:
    if not isinstance(arg, int):
        _LOG.warning("Invalid character argument: %s", type(arg))
        return "?"

    return _render_string(part, chr(arg % 256))


class Renderer(Protocol):
    def __call__(self, part: ResolvedSpecifierPart, arg: RawArg) -> str: ...


RENDERERS: Mapping[str, Renderer] = {
    "b": _render_integer,
    "d": _render_integer,
    "i": _render_integer,
    "u": _render_integer,  # Unsigned integer
    "o": _render_integer,  # Octal
    "x": _render_integer,  # Hexadecimal (lowercase)
    "X": _render_integer,  # Hexadecimal (uppercase)
    "p": _render_integer,  # Treat pointers as unsigned integers and format in hexadecimal
    "e": _render_float,
    "E": _render_float,
    "f": _render_float,
    "F": _render_float,
    "g": _render_float,
    "G": _render_float,
    "s": _render_string,
    "c": _render_char,
}


def _parse_specifier(data: ParseResults, *, raw: str) -> SpecifierPart:
    conversion_specifier = data["conversion_specifier"]

    if width_str := data.get("width"):
        width = PLACEHOLDER if width_str == PLACEHOLDER else int(width_str)
    else:
        width = None

    precision = None
    if conversion_specifier in {"a", "A", "e", "E", "f", "F"}:
        precision = 6

    if (precision_tup := data.get("precision")) is not None:
        precision_str = precision_tup[0] if precision_tup else None

        if precision_str == PLACEHOLDER:
            precision = PLACEHOLDER
        elif precision_str:
            precision = int(precision_str)
        else:
            # The C standard says that if the precision is omitted (i.e. just ".")
            # it should be treated as if it were zero.
            precision = 0

    return SpecifierPart(
        raw=raw,
        flags=data.get("flags", ""),
        width=width,
        precision=precision,
        length_modifier=data.get("length_modifier", ""),
        conversion_specifier=conversion_specifier,
    )


def parse_printf_format(fmt: str) -> Iterator[Part]:
    prev_end = 0
    for parse_results, start, end in PARSER.scanString(fmt):
        if prev_end < start:
            yield TextPart(raw=fmt[prev_end:start])

        if "conversion_specifier" not in parse_results:
            yield TextPart(raw="%")
        else:
            yield _parse_specifier(
                cast(ParseResults, parse_results.as_dict()),  # pyright: ignore[reportUnknownMemberType]
                raw=fmt[start:end],
            )

        prev_end = end

    if prev_end < len(fmt):
        yield TextPart(raw=fmt[prev_end:])


def parse_specifier(fmt: str) -> SpecifierPart:
    parts = tuple(parse_printf_format(fmt))
    assert len(parts) == 1
    rv = parts[0]
    assert isinstance(rv, SpecifierPart)
    return rv


Errors = Literal[
    "strict",  # raises for unknown conversion specifiers
    "normal",  # only raises for programming errors
    "safe",  # tries to never raise
]


class ArgError(Exception):
    pass


@dataclasses.dataclass
class ArgList:
    _args: Sequence[object]
    _idx: int = 0

    def pop(self) -> RawArg:
        idx, self._idx = self._idx, self._idx + 1

        try:
            rv = self._args[idx]
        except IndexError:
            raise ArgError(f"Missing argument at index {idx}") from None

        if not isinstance(rv, (str, float, int)):
            raise ArgError(f"Invalid argument type {type(rv)} at index {idx}")

        return rv


def _resolve_specifier(part: SpecifierPart, args: ArgList) -> tuple[ResolvedSpecifierPart, RawArg]:
    # NB: ensure we consume all args before performing any other logic
    updates = {k: args.pop() for k in ("width", "precision") if getattr(part, k) == PLACEHOLDER}
    arg = args.pop()

    if updates:
        for key, value in updates.items():
            if not isinstance(value, int):
                raise ArgError(f"Invalid {key!r} argument")

        part = dataclasses.replace(part, **updates)

    return cast(ResolvedSpecifierPart, part), arg


def _printf(fmt: str, args: Sequence[object], *, errors: Errors) -> Iterable[str]:
    """Yield the formatted string parts.

    Take the given fmt string, find the format specifiers, and yield strings
    consisting of:
    - all formatted args (each formatted according to the corresponding
      specifier)
    - all raw text around specifiers

    Example:
    >>> fmt = "Hello, %s! You have %d new messages."
    >>> args = ("world", 42)
    >>> list(_printf(fmt, *args))
    ["Hello, ", "world", "! You have ", "42", " new messages."]
    """
    arg_list = ArgList(args)

    for part in parse_printf_format(fmt):
        if isinstance(part, TextPart):
            yield part.raw
        elif isinstance(part, SpecifierPart):  # pyright: ignore[reportUnnecessaryIsInstance]
            try:
                part, arg = _resolve_specifier(part, arg_list)
            except ArgError:
                if errors == "strict":
                    raise
                yield part.raw
                continue

            try:
                renderer = RENDERERS[part.conversion_specifier]
            except KeyError:
                if errors == "strict":
                    raise
                yield part.raw
                continue

            try:
                item = renderer(part, arg)
            except Exception:
                if errors != "safe":
                    raise
                yield part.raw
                continue

            yield item
        else:
            assert_never(part)


def printf(fmt: str, args: Sequence[object], *, errors: Errors = "safe") -> str:
    return "".join(_printf(fmt, args, errors=errors))
