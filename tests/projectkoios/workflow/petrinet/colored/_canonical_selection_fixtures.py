"""Private canonical selection-result transport fixtures."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.canonical.selections import (
    CpnCanonicalSelectionResult,
    CpnCanonicalSelectionResultCodec,
    CpnCanonicalSelectionResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.selection import (
    CpnBindingSelectionRequest,
    CpnBindingSelector,
    CpnSelectionResult,
)


def selection_result() -> CpnSelectionResult:
    """Return one deterministic selected-binding result."""
    definition, enablement = selection_enablement(values=(1,))
    return CpnBindingSelector().execute(
        CpnBindingSelectionRequest(definition, enablement)
    )


def canonical_selection_result() -> CpnCanonicalSelectionResult:
    """Return exact canonical bytes for the synthetic selection result."""
    return CpnCanonicalSelectionResultCodec().encode(
        CpnCanonicalSelectionResultEncodingInput(selection_result())
    )
