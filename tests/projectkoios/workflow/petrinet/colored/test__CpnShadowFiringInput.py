"""Nominal tests for ``CpnShadowFiringInput``."""

import pytest

from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringInput,
)


def test_constructor__rejects_arbitrary_roots() -> None:
    with pytest.raises(TypeError):
        CpnShadowFiringInput(object(), object(), object(), object())  # type: ignore[arg-type]
