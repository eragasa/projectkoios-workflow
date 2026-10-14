"""Nominal tests for ``CpnCanonicalMarkingIdentity``."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingIdentity,
)


def test_constructor__requires_domain_separated_sha256() -> None:
    value = "projectkoios.workflow.cpn-marking:0.1:" + "0" * 64
    assert CpnCanonicalMarkingIdentity(value).value == value
    with pytest.raises(ValueError):
        CpnCanonicalMarkingIdentity("0" * 64)
