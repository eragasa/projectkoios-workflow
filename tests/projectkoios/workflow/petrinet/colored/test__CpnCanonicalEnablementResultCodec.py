import json

import pytest

from _canonical_enablement_fixtures import (
    canonical_enablement_result,
    enablement_result,
    failed_enablement_context,
)
from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResult,
    CpnCanonicalEnablementResultCodec,
    CpnCanonicalEnablementResultDecodingInput,
    CpnCanonicalEnablementResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)


def test_decode__round_trips_complete_success_result() -> None:
    result = CpnCanonicalEnablementResultCodec().decode(
        CpnCanonicalEnablementResultDecodingInput(canonical_enablement_result())
    )
    assert result.result == enablement_result()


def test_decode__round_trips_structured_failure_result() -> None:
    definition, marking, source = failed_enablement_context()
    document = CpnCanonicalEnablementResultCodec().encode(
        CpnCanonicalEnablementResultEncodingInput(source, definition, marking)
    )
    result = CpnCanonicalEnablementResultCodec().decode(
        CpnCanonicalEnablementResultDecodingInput(document)
    )
    assert result.result == source


def test_decode__rejects_asserted_result_identity() -> None:
    state = json.loads(canonical_enablement_result().canonical_bytes)
    state["result_identity"] = "a" * 64
    document = CpnCanonicalEnablementResult(
        json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalEnablementResultCodec().decode(
            CpnCanonicalEnablementResultDecodingInput(document)
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH


def test_decode__rejects_noncanonical_binding_order() -> None:
    state = json.loads(canonical_enablement_result().canonical_bytes)
    state["enabled_binding_canonical_bytes_hex"] *= 2
    document = CpnCanonicalEnablementResult(
        json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalEnablementResultCodec().decode(
            CpnCanonicalEnablementResultDecodingInput(document)
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.INVALID_SHAPE
