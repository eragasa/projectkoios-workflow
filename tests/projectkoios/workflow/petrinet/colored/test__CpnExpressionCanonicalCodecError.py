from projectkoios.workflow.petrinet.colored.canonical.expressions.errors import (
    CpnExpressionCanonicalCodecError,
)

SUT = CpnExpressionCanonicalCodecError


def test_public_error__retains_nominal_exception_boundary() -> None:
    assert issubclass(SUT, ValueError)
    assert SUT is not ValueError
