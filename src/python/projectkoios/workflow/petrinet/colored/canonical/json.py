"""Strict bounded canonical JSON parsing primitives."""

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import final


type CpnCanonicalJsonValue = (
    None
    | bool
    | str
    | list["CpnCanonicalJsonValue"]
    | dict[str, "CpnCanonicalJsonValue"]
)


class CpnCanonicalCodecErrorCode(StrEnum):
    """Closed translated failures from canonical transport."""

    INVALID_ARGUMENT = "invalid_argument"
    DOCUMENT_TOO_LARGE = "document_too_large"
    INVALID_UTF8 = "invalid_utf8"
    INVALID_JSON = "invalid_json"
    DUPLICATE_KEY = "duplicate_key"
    NONCANONICAL_BYTES = "noncanonical_bytes"
    UNSUPPORTED_PROFILE = "unsupported_profile"
    INVALID_SHAPE = "invalid_shape"
    INVALID_FIELD = "invalid_field"
    BOUND_EXCEEDED = "bound_exceeded"
    SCHEMA_VIOLATION = "schema_violation"
    IDENTITY_MISMATCH = "identity_mismatch"


class CpnCanonicalCodecError(ValueError):
    """One bounded inspectable canonical transport failure."""

    def __init__(
        self,
        code: CpnCanonicalCodecErrorCode,
        path: tuple[str, ...],
        diagnostic: str,
    ) -> None:
        if not isinstance(code, CpnCanonicalCodecErrorCode):
            raise TypeError("code must be CpnCanonicalCodecErrorCode")
        if type(path) is not tuple or any(
            type(item) is not str for item in path
        ):
            raise TypeError("path must be a tuple of strings")
        if type(diagnostic) is not str or not diagnostic:
            raise TypeError("diagnostic must be a nonempty string")
        self.code = code
        self.path = path
        self.diagnostic = diagnostic
        super().__init__(
            f"{code.value} at {'.'.join(path) or '$'}: {diagnostic}"
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalJsonParserIdentity:
    """Identity of exact UTF-8 canonical JSON parsing semantics."""

    value: str = "projectkoios.workflow.cpn.canonical-json-parser:0.1"


@dataclass(frozen=True, slots=True)
class CpnCanonicalJsonParsingInput:
    """Exact bounded bytes to parse and recanonicalize."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")


@dataclass(frozen=True, slots=True)
class CpnCanonicalJsonParsingResult:
    """Exact immutable bytes that passed strict canonical JSON admission."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")


@final
class CpnCanonicalJsonParser:
    """Directly reject invalid UTF-8, numbers, duplicates, and noncanonical JSON."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalJsonParserIdentity:
        """Return the exact parser semantics identity."""
        return CpnCanonicalJsonParserIdentity()

    def execute(
        self, parsing_input: CpnCanonicalJsonParsingInput
    ) -> CpnCanonicalJsonParsingResult:
        """Parse and require byte-for-byte canonical JSON equality."""
        if type(parsing_input) is not CpnCanonicalJsonParsingInput:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "parsing_input must be CpnCanonicalJsonParsingInput",
            )
        try:
            text = parsing_input.canonical_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_UTF8,
                (),
                "document is not valid UTF-8",
            ) from exc
        try:
            paired_state = json.loads(text, object_pairs_hook=tuple)
            pending: list[object] = [paired_state]
            while pending:
                current = pending.pop()
                if type(current) is tuple:
                    keys: set[str] = set()
                    for pair in current:
                        if (
                            type(pair) is not tuple
                            or len(pair) != 2
                            or type(pair[0]) is not str
                        ):
                            raise CpnCanonicalCodecError(
                                CpnCanonicalCodecErrorCode.INVALID_JSON,
                                (),
                                "invalid object-pair representation",
                            )
                        if pair[0] in keys:
                            raise CpnCanonicalCodecError(
                                CpnCanonicalCodecErrorCode.DUPLICATE_KEY,
                                (pair[0],),
                                "duplicate object key",
                            )
                        keys.add(pair[0])
                        pending.append(pair[1])
                elif type(current) is list:
                    pending.extend(current)
                elif type(current) in (int, float):
                    raise CpnCanonicalCodecError(
                        CpnCanonicalCodecErrorCode.INVALID_JSON,
                        (),
                        "raw JSON numbers are unsupported",
                    )
                elif current is not None and type(current) not in (bool, str):
                    raise CpnCanonicalCodecError(
                        CpnCanonicalCodecErrorCode.INVALID_JSON,
                        (),
                        "unsupported JSON value",
                    )
            state: CpnCanonicalJsonValue = json.loads(text)
            recanonical = json.dumps(
                state,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except CpnCanonicalCodecError:
            raise
        except (
            json.JSONDecodeError,
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_JSON,
                (),
                "document is not valid canonical JSON",
            ) from exc
        if recanonical != parsing_input.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "document bytes do not match canonical JSON",
            )
        return CpnCanonicalJsonParsingResult(parsing_input.canonical_bytes)
