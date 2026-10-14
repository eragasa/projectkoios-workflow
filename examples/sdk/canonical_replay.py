"""Encode and deterministically replay one canonical firing result."""

from _support import execution_profile, selected_firing_input
from projectkoios.workflow.petrinet.colored.canonical.firing.results.codec import (
    CpnCanonicalFiringResultCodec,
)
from projectkoios.workflow.petrinet.colored.canonical.firing.results.documents import (
    CpnCanonicalFiringResultDecodingInput,
    CpnCanonicalFiringResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.firing.transitions import (
    CpnTransitionFirer,
)


def main() -> None:
    """Retain canonical bytes and verify replay under the exact profile."""
    profile = execution_profile()
    result = CpnTransitionFirer().execute(selected_firing_input())
    codec = CpnCanonicalFiringResultCodec()
    document = codec.encode(
        CpnCanonicalFiringResultEncodingInput(result, profile)
    )
    replay = codec.decode(
        CpnCanonicalFiringResultDecodingInput(document, profile)
    )
    assert replay.result == result
    print(document.identity.value)


if __name__ == "__main__":
    main()
