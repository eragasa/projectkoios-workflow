import json

import pytest

from _canonical_directive_fixtures import canonical_directive, directive
from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirective,
    CpnCanonicalSelectionDirectiveCodec,
    CpnCanonicalSelectionDirectiveDecodingInput,
)
from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)


def test_decode__round_trips_exact_directive() -> None:
    result = CpnCanonicalSelectionDirectiveCodec().decode(
        CpnCanonicalSelectionDirectiveDecodingInput(canonical_directive())
    )
    assert result.directive == directive()


def test_decode__rejects_asserted_directive_identity() -> None:
    state = json.loads(canonical_directive().canonical_bytes)
    state["directive_identity"] = "a" * 64
    document = CpnCanonicalSelectionDirective(
        json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalSelectionDirectiveCodec().decode(
            CpnCanonicalSelectionDirectiveDecodingInput(document)
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH
