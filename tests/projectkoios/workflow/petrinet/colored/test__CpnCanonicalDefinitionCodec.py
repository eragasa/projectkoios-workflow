"""Direct tests for complete flat-definition canonical transport."""

from dataclasses import replace

from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionDecodingInput,
    CpnCanonicalDefinitionEncodingInput,
)

from projectkoios.workflow.petrinet.colored.definitions import CpnPlaceIdentity
from projectkoios.workflow.petrinet.colored.validation.definitions import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)

from _validation_fixtures import valid_definition


def test_encode_decode__round_trips_complete_scalar_definition() -> None:
    """Every flat topology and expression field reconstructs exactly."""
    codec = CpnCanonicalDefinitionCodec()
    document = codec.encode(
        CpnCanonicalDefinitionEncodingInput(valid_definition())
    )
    result = codec.decode(CpnCanonicalDefinitionDecodingInput(document))
    assert result.definition == valid_definition()
    assert result.document == document


def test_encode__keeps_transport_distinct_from_structural_validation() -> None:
    source = valid_definition()
    definition = replace(
        source,
        arcs=(
            replace(
                source.arcs[0], place_identity=CpnPlaceIdentity("unknown-place")
            ),
        ),
    )
    assert (
        not CpnDefinitionValidator()
        .execute(CpnDefinitionValidationRequest(definition))
        .is_valid
    )
    codec = CpnCanonicalDefinitionCodec()
    document = codec.encode(CpnCanonicalDefinitionEncodingInput(definition))
    decoded = codec.decode(CpnCanonicalDefinitionDecodingInput(document))
    assert decoded.definition == definition
    assert (
        not CpnDefinitionValidator()
        .execute(CpnDefinitionValidationRequest(decoded.definition))
        .is_valid
    )


def test_encode__semantic_mutation_changes_identity() -> None:
    """Selection-policy/topology semantic bytes cannot retain an old identity."""
    from projectkoios.workflow.petrinet.colored.definitions import (
        CpnSelectionPolicy,
    )

    definition = valid_definition()
    directed = replace(
        definition,
        selection_policy=CpnSelectionPolicy.DIRECTED_ALLOWED,
    )
    codec = CpnCanonicalDefinitionCodec()
    assert (
        codec.encode(CpnCanonicalDefinitionEncodingInput(definition)).identity
        != codec.encode(CpnCanonicalDefinitionEncodingInput(directed)).identity
    )
