"""Nominal tests for ``CpnCanonicalMarkingDecodingInput``."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingDecodingInput,
)


def test_constructor__rejects_arbitrary_roots() -> None:
    with pytest.raises(TypeError):
        CpnCanonicalMarkingDecodingInput(object(), object())  # type: ignore[arg-type]
