from __future__ import annotations

import dataclasses
import decimal
import logging
from collections.abc import Sequence
from enum import IntEnum

import cbor2
import click

from mflt_compact_log.printf import printf

log = logging.getLogger(__name__)


class UnpackCompactLogError(ValueError):
    pass


class CompactLogDecodeError(ValueError):
    pass


class CompactLogPromotionType(IntEnum):
    UNSET = -1
    INT32 = 0
    INT64 = 1
    DOUBLE = 2
    STRING = 3


@dataclasses.dataclass
class CompactLogArg:
    arg_type: CompactLogPromotionType
    value: object


@dataclasses.dataclass
class UnpackedCompactLog:
    log_id: int
    va_args: list[CompactLogArg]


class CompactLogDecoder:
    @staticmethod
    def unpack_compact_log(input_args: Sequence[object]) -> UnpackedCompactLog:
        """
        Unpacks CBOR encoded "compact logs" into the log_id & a va_arg array

        where,
         - log_id The id used to recover the C fmt string from an ELF
         - va_args A list of [ argument type, argument value ]

        The argument type is no longer used in the Python implementation but
        we're keeping it for now for backwards compatibility.

        More details about the encoding scheme in:
          sdk/embedded/components/log/src/memfault_compact_log_serializer.c
        """
        args = iter(input_args)
        log_fmt_id = next(args)
        if not isinstance(log_fmt_id, int):
            raise UnpackCompactLogError(f"Expected log_fmt_id to be an int, got {log_fmt_id}")
        assert isinstance(log_fmt_id, int)

        arg_list: list[CompactLogArg] = [
            CompactLogArg(CompactLogPromotionType.UNSET, arg[0] if isinstance(arg, list) else arg)
            for arg in args
        ]

        return UnpackedCompactLog(log_fmt_id, arg_list)

    def decode(
        self, c_fmt: str, va_args: list[CompactLogArg], *, max_result_len: int = 512
    ) -> bytes:
        """
        Converts compact log to a full byte string given a C fmt string & arg list

        Args:
          c_fmt: A format string suitable for libc's printf family of functions
          va_args: Argument output from unpack_compact_log
          max_result_len: Maximum length string to generate before truncating decode
        """
        try:
            formatted_string = printf(c_fmt, [arg.value for arg in va_args]).encode()
        except ValueError as err:
            raise CompactLogDecodeError("Failed to decode compact log") from err

        # Truncate then split on null byte to simulate C-style string behavior
        # Note that we pass `-1` here as the *real* printf would always have a
        # null terminator at the end of the string, which this implementation
        # does not.
        result = formatted_string[: max_result_len - 1]
        return result.split(b"\x00")[0]

    @classmethod
    def from_cbor_array(cls, fmt_str: str, compact_log: bytes | bytearray | memoryview):
        """
        Helper for 1-off decoding a compact log.
        """
        try:
            args: object = cbor2.loads(compact_log, tag_hook=tag_hook)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        except (
            UnicodeDecodeError,
            ValueError,
            RecursionError,
            TypeError,
            LookupError,
            OSError,
            OverflowError,
            decimal.InvalidOperation,
            MemoryError,
        ) as e:
            raise cbor2.CBORDecodeValueError(str(e)) from e

        va_args = cls.unpack_compact_log(args).va_args  # pyright: ignore[reportArgumentType]
        compact_log_decoder = cls()
        return compact_log_decoder.decode(fmt_str, va_args)

    @classmethod
    def from_arg_list(cls, fmt_str: str, args: list[object]):
        """
        Helper for 1-off decoding a format log that has been deserialized from cbor
        """
        va_args = cls.unpack_compact_log(args).va_args
        compact_log_decoder = cls()
        return compact_log_decoder.decode(fmt_str, va_args)


def tag_hook(decoder: cbor2.CBORDecoder, tag: cbor2.CBORTag) -> object:
    if decoder.immutable:
        # We received a tagged value inside in a context where Python requires values
        # to be hashable (e.g. keys for a mapping). We need to bail here.
        raise cbor2.CBORDecodeValueError(f"Unsupported/unknown tagged value in mapping: {tag.tag}")

    return tag


@click.command()
@click.version_option()
@click.argument("fmt")
@click.argument("compact-log")
def main(fmt: str, compact_log: str):
    """
    Given a fmt string and hex string encoded compact log, recover original
    string

    Example Usage:

    \b
    $ python compact.py "An Integer Format String: %d" 820A0B
        Log Recovered:
        An Integer Format String: 11

    """
    compact_log_as_bytes = bytes.fromhex(compact_log)
    log = CompactLogDecoder.from_cbor_array(fmt, compact_log_as_bytes)
    click.secho("Log Recovered:")
    click.secho(log.decode(), fg="green")


if __name__ == "__main__":
    main()
