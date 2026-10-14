"""Software verification of the canonical JSON parser owner."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)

SUT = CpnCanonicalJsonParser


def test_method__execute__canonical_document__retains_exact_bytes() -> None:
    canonical_bytes = b'{"kind":"record","values":[null,true,"value"]}'

    result = SUT().execute(CpnCanonicalJsonParsingInput(canonical_bytes))

    assert result.canonical_bytes == canonical_bytes
    assert SUT().identity.value == (
        "projectkoios.workflow.cpn.canonical-json-parser:0.1"
    )


@pytest.mark.parametrize(
    ("canonical_bytes", "expected_code"),
    (
        (
            b'{"key":"first","key":"second"}',
            CpnCanonicalCodecErrorCode.DUPLICATE_KEY,
        ),
        (b'{"value":1}', CpnCanonicalCodecErrorCode.INVALID_JSON),
        (
            b'{"second":true,"first":false}',
            CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
        ),
    ),
)
def test_method__execute__owned_json_semantics__reject_invalid_document(
    canonical_bytes: bytes,
    expected_code: CpnCanonicalCodecErrorCode,
) -> None:
    with pytest.raises(CpnCanonicalCodecError) as captured:
        SUT().execute(CpnCanonicalJsonParsingInput(canonical_bytes))

    assert captured.value.code is expected_code
