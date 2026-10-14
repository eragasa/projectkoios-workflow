"""Direct tests for exact canonical marking encoding."""

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingDecodingInput,
    CpnCanonicalMarkingEncodingInput,
)
from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinition,
    CpnDefinitionIdentity,
    CpnPlaceIdentity,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnToken,
    CpnValue,
    CpnValueKind,
)


def marking(identity: str = "marking") -> CpnMarking:
    """Return one bounded canonicalizable marking."""
    return CpnMarking(
        CpnMarkingIdentity(identity),
        CpnDefinitionIdentity("definition"),
        (
            CpnPlaceMarking(
                CpnPlaceIdentity("place"),
                (
                    CpnToken(
                        CpnColorIdentity("color"),
                        CpnValue(CpnValueKind.INTEGER, 2),
                    ),
                ),
            ),
        ),
    )


def test_encode__binds_exact_marking_bytes_and_nominal_identity() -> None:
    """The canonical digest changes with represented marking state."""
    codec = CpnCanonicalMarkingCodec()
    first = codec.encode(CpnCanonicalMarkingEncodingInput(marking()))
    replay = codec.encode(CpnCanonicalMarkingEncodingInput(marking()))
    changed = codec.encode(CpnCanonicalMarkingEncodingInput(marking("changed")))
    assert first == replay
    assert first.identity != changed.identity
    assert first.sha256 == first.identity.value.rsplit(":", 1)[-1]


def test_decode__reconstructs_from_canonical_bytes() -> None:
    source = marking()
    definition = CpnDefinition(
        source.definition_identity,
        (),
        (),
        (),
        (),
        (),
    )
    document = CpnCanonicalMarkingCodec().encode(
        CpnCanonicalMarkingEncodingInput(source)
    )
    result = CpnCanonicalMarkingCodec().decode(
        CpnCanonicalMarkingDecodingInput(document, definition)
    )
    assert result.marking == source
    assert result.document == document
