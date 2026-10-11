"""Nominal tests for ``CpnCanonicalMarkingDecodingResult``."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingDecodingResult,
)


def test_constructor__rejects_arbitrary_roots() -> None:
    with pytest.raises(TypeError):
        CpnCanonicalMarkingDecodingResult(object(), object())  # type: ignore[arg-type]
