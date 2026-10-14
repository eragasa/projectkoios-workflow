"""Nominal tests for ``CpnCanonicalMarking``."""

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarking,
)


def test_constructor__derives_exact_content_identity() -> None:
    document = CpnCanonicalMarking(b"{}")
    assert document.sha256 == document.identity.value.rsplit(":", 1)[-1]
