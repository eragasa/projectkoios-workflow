from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
)

SUT = CpnCanonicalCodecError


def test_public_error__retains_nominal_exception_boundary() -> None:
    assert issubclass(SUT, ValueError)
    assert SUT is not ValueError
