"""Nominal tests for ``CpnCanonicalMarkingEncodingInput``."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingEncodingInput,
)


def test_constructor__rejects_non_marking() -> None:
    with pytest.raises(TypeError):
        CpnCanonicalMarkingEncodingInput(object())  # type: ignore[arg-type]
