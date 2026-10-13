"""Enable, select, and purely fire one transition."""

from _support import selected_firing_input
from projectkoios.workflow.petrinet.colored.firing.results import (
    CpnFiringOutcomeKind,
)
from projectkoios.workflow.petrinet.colored.firing.transitions import (
    CpnTransitionFirer,
)


def main() -> None:
    """Construct a complete firing request and inspect its typed result."""
    firing_input = selected_firing_input()
    result = CpnTransitionFirer().execute(firing_input)
    if result.outcome is not CpnFiringOutcomeKind.SUCCESS:
        raise RuntimeError(f"firing failed: {result.failure!r}")
    if result.successor_marking is None:
        raise RuntimeError("success omitted its successor marking")
    produced = result.successor_marking.places[0].tokens[0]
    assert produced.value.value == 2
    print(result.identity.value)


if __name__ == "__main__":
    main()
