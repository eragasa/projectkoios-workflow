"""Private canonical binding transport fixtures."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.bindings import CpnBinding
from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBinding,
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingEncodingInput,
)


def binding() -> CpnBinding:
    """Return one enabled binding with a scalar assignment."""
    _, enablement = selection_enablement(values=(1,))
    assert enablement.enabled_bindings is not None
    return enablement.enabled_bindings[0]


def canonical_binding() -> CpnCanonicalBinding:
    """Return exact canonical bytes for the synthetic binding."""
    return CpnCanonicalBindingCodec().encode(
        CpnCanonicalBindingEncodingInput(binding())
    )
