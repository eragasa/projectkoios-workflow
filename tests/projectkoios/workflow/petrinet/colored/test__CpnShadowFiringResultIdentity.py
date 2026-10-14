"""Nominal tests for ``CpnShadowFiringResultIdentity``."""

import pytest

from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringResultIdentity,
)


def test_constructor__requires_domain_separated_sha256() -> None:
    value = "projectkoios.workflow.cpn-shadow-firing-result:0.1:" + "0" * 64
    assert CpnShadowFiringResultIdentity(value).value == value
    with pytest.raises(ValueError):
        CpnShadowFiringResultIdentity("0" * 64)
