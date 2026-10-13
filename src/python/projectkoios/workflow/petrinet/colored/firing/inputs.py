"""Immutable complete input for one pure CPN firing attempt."""

from __future__ import annotations
from dataclasses import dataclass
from ..definitions import CpnDefinition
from ..enablement.outcomes import (
    CpnEnablementResult,
)
from ..bindings import CpnBinding
from ..definitions import CpnTransitionIdentity
from ..markings import CpnMarking
from ..selection import CpnSelectionDirectiveIdentity, CpnSelectionResult


@dataclass(frozen=True, slots=True)
class CpnFiringInput:
    """Exact immutable derivation inputs for one pure firing attempt."""

    definition: CpnDefinition
    transition_identity: CpnTransitionIdentity
    predecessor_marking: CpnMarking
    enablement_result: CpnEnablementResult
    selection_result: CpnSelectionResult
    selected_binding: CpnBinding
    directive_identity: CpnSelectionDirectiveIdentity | None
    external_output_binding: CpnBinding

    def __post_init__(self) -> None:
        """Validate exact public nominal argument types only."""
        expected = (
            ("definition", CpnDefinition),
            ("transition_identity", CpnTransitionIdentity),
            ("predecessor_marking", CpnMarking),
            ("enablement_result", CpnEnablementResult),
            ("selection_result", CpnSelectionResult),
            ("selected_binding", CpnBinding),
            ("external_output_binding", CpnBinding),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.directive_identity is not None and (
            type(self.directive_identity) is not CpnSelectionDirectiveIdentity
        ):
            raise TypeError(
                "directive_identity must be CpnSelectionDirectiveIdentity "
                "or None"
            )
