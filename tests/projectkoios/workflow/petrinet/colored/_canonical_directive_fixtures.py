"""Private canonical selection-directive transport fixtures."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirective,
    CpnCanonicalSelectionDirectiveCodec,
    CpnCanonicalSelectionDirectiveEncodingInput,
)
from projectkoios.workflow.petrinet.colored.selection import (
    CpnSelectionDirective,
)


def directive() -> CpnSelectionDirective:
    """Return one explicit directive for an exact enabled binding."""
    _, enablement = selection_enablement(values=(1,))
    assert enablement.enabled_bindings is not None
    return CpnSelectionDirective(
        enablement.identity, enablement.enabled_bindings[0]
    )


def canonical_directive() -> CpnCanonicalSelectionDirective:
    """Return exact canonical bytes for the synthetic directive."""
    return CpnCanonicalSelectionDirectiveCodec().encode(
        CpnCanonicalSelectionDirectiveEncodingInput(directive())
    )
