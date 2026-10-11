import json

import pytest

from _canonical_selection_fixtures import (
    canonical_selection_result,
    selection_result,
)
from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)
from projectkoios.workflow.petrinet.colored.canonical.selections import (
    CpnCanonicalSelectionResult,
    CpnCanonicalSelectionResultCodec,
    CpnCanonicalSelectionResultDecodingInput,
)


def test_decode__round_trips_exact_selected_result() -> None:
    result = CpnCanonicalSelectionResultCodec().decode(
        CpnCanonicalSelectionResultDecodingInput(canonical_selection_result())
    )
    assert result.result == selection_result()


def test_decode__rejects_asserted_result_identity() -> None:
    state = json.loads(canonical_selection_result().canonical_bytes)
    state["result_identity"] = "a" * 64
    document = CpnCanonicalSelectionResult(
        json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalSelectionResultCodec().decode(
            CpnCanonicalSelectionResultDecodingInput(document)
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH
