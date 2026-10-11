"""Nominal tests for ``CpnEnablementResultIdentityDerivationInput``."""

import pytest

from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementResultIdentityDerivationInput,
)


def test_constructor__rejects_arbitrary_roots() -> None:
    with pytest.raises(TypeError):
        CpnEnablementResultIdentityDerivationInput(
            object(), object(), object(), object(), object(), (), None
        )  # type: ignore[arg-type]
