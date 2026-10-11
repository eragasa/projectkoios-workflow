"""Private canonical enablement-result transport fixtures."""

from _firing_fixtures import predecessor
from _selection_fixtures import selection_definition, selection_enablement

from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResult,
    CpnCanonicalEnablementResultCodec,
    CpnCanonicalEnablementResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinition,
    CpnDefinitionIdentity,
)
from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementResult,
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)


def enablement_context() -> tuple[
    CpnDefinition, CpnMarking, CpnEnablementResult
]:
    """Return exact definition, marking, and successful enablement."""
    definition, _ = selection_enablement(values=(1,))
    marking = predecessor(definition)
    return (
        definition,
        marking,
        CpnTransitionEnabler().execute(
            CpnTransitionEnablementRequest(definition, marking)
        ),
    )


def enablement_result() -> CpnEnablementResult:
    """Return one successful complete enablement result."""
    return enablement_context()[2]


def failed_enablement_context() -> tuple[
    CpnDefinition, CpnMarking, CpnEnablementResult
]:
    """Return exact definition, invalid marking, and failure result."""
    definition = selection_definition()
    marking = CpnMarking(
        CpnMarkingIdentity("invalid-marking"),
        CpnDefinitionIdentity("other-definition"),
        tuple(CpnPlaceMarking(item.identity, ()) for item in definition.places),
    )
    return (
        definition,
        marking,
        CpnTransitionEnabler().execute(
            CpnTransitionEnablementRequest(definition, marking)
        ),
    )


def failed_enablement_result() -> CpnEnablementResult:
    """Return one structured invalid-marking enablement failure."""
    return failed_enablement_context()[2]


def canonical_enablement_result() -> CpnCanonicalEnablementResult:
    """Return exact canonical bytes for the synthetic enablement result."""
    definition, marking, result = enablement_context()
    return CpnCanonicalEnablementResultCodec().encode(
        CpnCanonicalEnablementResultEncodingInput(result, definition, marking)
    )
