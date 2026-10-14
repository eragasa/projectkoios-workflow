"""Private bounded validation and deterministic identity helpers."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence

MAX_IDENTITY_BYTES = 512
MAX_ROLE_BYTES = 128
MAX_TEXT_BYTES = 512
MAX_MEDIA_TYPE_BYTES = 255
MAX_CONTRACTS = 64
MAX_PAYLOAD_COUNT = 64
MAX_INLINE_PAYLOAD_BYTES = 4 * 1024 * 1024
MAX_TOTAL_PAYLOAD_BYTES = 16 * 1024 * 1024
MAX_REASON_COUNT = 64
MAX_DOCUMENT_BYTES = 32 * 1024 * 1024
MAX_DOCUMENT_DEPTH = 16
MAX_SIGNED_64 = 2**63 - 1

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*\Z", re.ASCII)
_MEDIA_TYPE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/"
    r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*\Z",
    re.ASCII,
)
_DRIVE_PREFIX = re.compile(r"[A-Za-z]:")


def validate_identity(value: object, label: str) -> str:
    """Return one bounded path-free ASCII identity."""
    text = validate_ascii_text(value, label, MAX_IDENTITY_BYTES)
    lowered = text.lower()
    if (
        text.startswith(("/", "~", "\\", "./", "../"))
        or text in {".", ".."}
        or "\\" in text
        or lowered.startswith("file:")
        or _DRIVE_PREFIX.match(text) is not None
        or "/" in text
    ):
        raise ValueError(f"{label} must not be a machine path")
    return text


def validate_sha256(value: object, label: str) -> str:
    """Return one lowercase hexadecimal SHA-256 spelling."""
    if type(value) is not str:
        raise TypeError(f"{label} must be a built-in str")
    if _SHA256.fullmatch(value) is None:
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def validate_ascii_text(value: object, label: str, maximum: int) -> str:
    """Return one nonempty stripped bounded ASCII string without controls."""
    if type(value) is not str:
        raise TypeError(f"{label} must be a built-in str")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and stripped")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError(f"{label} must contain ASCII only") from error
    if len(encoded) > maximum:
        raise ValueError(f"{label} exceeds {maximum} ASCII bytes")
    if any(byte < 0x20 or byte == 0x7F for byte in encoded):
        raise ValueError(f"{label} must not contain controls or DEL")
    return value


def validate_token(value: object, label: str, maximum: int = MAX_ROLE_BYTES) -> str:
    """Return one bounded ASCII token."""
    text = validate_ascii_text(value, label, maximum)
    if _TOKEN.fullmatch(text) is None:
        raise ValueError(f"{label} has an invalid token grammar")
    return text


def validate_media_type(value: object) -> str:
    """Return one canonical media type without parameters."""
    text = validate_ascii_text(value, "media_type", MAX_MEDIA_TYPE_BYTES)
    if text != text.lower() or _MEDIA_TYPE.fullmatch(text) is None:
        raise ValueError("media_type must be one lowercase type/subtype")
    return text


def validate_nonnegative_int(value: object, label: str) -> int:
    """Return one exact nonnegative signed-64 integer."""
    if type(value) is not int:
        raise TypeError(f"{label} must be a built-in int")
    if not 0 <= value <= MAX_SIGNED_64:
        raise ValueError(f"{label} must be a nonnegative signed-64 integer")
    return value


def validate_positive_int(value: object, label: str, maximum: int) -> int:
    """Return one exact positive bounded integer."""
    if type(value) is not int:
        raise TypeError(f"{label} must be a built-in int")
    if not 1 <= value <= maximum:
        raise ValueError(f"{label} must be in 1..{maximum}")
    return value


def validate_sdk_version(value: object, expected: str) -> str:
    """Require the exact SDK contract version."""
    if type(value) is not str:
        raise TypeError("sdk_contract_version must be a built-in str")
    if value != expected:
        raise ValueError("unsupported SDK contract version")
    return value


def semantic_sha256(domain: str, value: object) -> str:
    """Hash one private deterministic semantic JSON preimage."""
    payload = json.dumps(
        {"domain": domain, "value": value},
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def closed_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    """Require one exact mapping key set."""
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{label} keys differ; missing={missing}, extra={extra}")


def validate_depth(value: object, depth: int = 1) -> None:
    """Reject JSON structures deeper than the SDK bound."""
    if depth > MAX_DOCUMENT_DEPTH:
        raise ValueError("document exceeds maximum JSON depth")
    if type(value) is dict:
        for nested in value.values():
            validate_depth(nested, depth + 1)
    elif type(value) is list:
        for nested in value:
            validate_depth(nested, depth + 1)


def require_mapping(value: object, label: str) -> dict[str, object]:
    """Require an exact built-in JSON object."""
    if type(value) is not dict:
        raise TypeError(f"{label} must be an object")
    if any(type(key) is not str for key in value):
        raise TypeError(f"{label} keys must be strings")
    return value


def require_array(value: object, label: str) -> list[object]:
    """Require an exact built-in JSON array."""
    if type(value) is not list:
        raise TypeError(f"{label} must be an array")
    return value


def require_string(value: object, label: str) -> str:
    """Require an exact built-in JSON string."""
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    return value


def require_integer(value: object, label: str) -> int:
    """Require an exact built-in JSON integer, excluding Boolean."""
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    return value


def require_tuple(
    value: object,
    item_type: type[object],
    label: str,
    maximum: int,
) -> tuple[object, ...]:
    """Require one bounded exact tuple of exact item types."""
    if type(value) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if len(value) > maximum:
        raise ValueError(f"{label} exceeds {maximum} entries")
    if any(type(item) is not item_type for item in value):
        raise TypeError(f"{label} contains an invalid item type")
    return value


def unique(values: Sequence[object], label: str) -> None:
    """Require values to be unique."""
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")
