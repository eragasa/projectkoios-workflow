import json
from dataclasses import replace

import pytest

from _canonical_firing_result_fixtures import (
    canonical_firing_result,
    execution_profile,
    failed_firing_result,
    firing_result,
)
from projectkoios.workflow.petrinet.colored.canonical.firing_results.documents import (
    CpnCanonicalFiringResult,
    CpnCanonicalFiringResultDecodingInput,
    CpnCanonicalFiringResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.canonical.firing_results.codec import (
    CpnCanonicalFiringResultCodec,
)
from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)


def test_decode__round_trips_result_by_pure_replay() -> None:
    result = CpnCanonicalFiringResultCodec().decode(
        CpnCanonicalFiringResultDecodingInput(
            canonical_firing_result(), execution_profile()
        )
    )
    assert result.result == firing_result()


def test_decode__round_trips_structured_failure_by_pure_replay() -> None:
    source = failed_firing_result()
    document = CpnCanonicalFiringResultCodec().encode(
        CpnCanonicalFiringResultEncodingInput(source, execution_profile())
    )
    result = CpnCanonicalFiringResultCodec().decode(
        CpnCanonicalFiringResultDecodingInput(document, execution_profile())
    )
    assert result.result == source


def test_decode__rejects_substituted_retained_profile_component() -> None:
    substituted_profile = replace(
        execution_profile(),
        transition_firer_identity="projectkoios.workflow.cpn.transition-firer:forged",
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalFiringResultCodec().decode(
            CpnCanonicalFiringResultDecodingInput(
                canonical_firing_result(), substituted_profile
            )
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH


def test_decode__rejects_asserted_result_identity() -> None:
    state = json.loads(canonical_firing_result().canonical_bytes)
    state["result_identity"] = "a" * 64
    document = CpnCanonicalFiringResult(
        json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalFiringResultCodec().decode(
            CpnCanonicalFiringResultDecodingInput(document, execution_profile())
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH
