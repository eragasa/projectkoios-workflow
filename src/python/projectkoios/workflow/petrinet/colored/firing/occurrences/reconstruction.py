"""Deterministic reconstruction of predecessor token occurrences."""

from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import final
from ...definitions import CpnArcDefinition, CpnDefinition
from ...expressions.grammar import CpnInputMode, CpnTokenPattern
from ...bindings import CpnBinding
from ...markings import CpnMarking
from ...values import CpnToken
from ..audits import CpnInhibitorEvaluation, CpnTokenOccurrence


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrenceReconstructionRequest:
    """Complete immutable state for one occurrence reconstruction."""

    definition: CpnDefinition
    marking: CpnMarking
    binding: CpnBinding

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.marking) is not CpnMarking:
            raise TypeError("marking must be CpnMarking")
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrenceReconstructionSuccess:
    """One feasible deterministic occurrence reconstruction."""

    consumed: tuple[CpnTokenOccurrence, ...]
    read: tuple[CpnTokenOccurrence, ...]
    inhibitors: tuple[CpnInhibitorEvaluation, ...]


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrenceReconstructionFailure:
    """Explicit absence of a feasible occurrence reconstruction."""

    reason: str

    def __post_init__(self) -> None:
        if type(self.reason) is not str or not self.reason:
            raise TypeError("reason must be a nonempty string")


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrenceReconstructionResponse:
    """Exactly one success or failure reconstruction response."""

    success: CpnTokenOccurrenceReconstructionSuccess | None = None
    failure: CpnTokenOccurrenceReconstructionFailure | None = None

    def __post_init__(self) -> None:
        if (self.success is None) == (self.failure is None):
            raise ValueError("exactly one reconstruction response is required")
        if (
            self.success is not None
            and type(self.success)
            is not CpnTokenOccurrenceReconstructionSuccess
        ):
            raise TypeError("success has the wrong type")
        if (
            self.failure is not None
            and type(self.failure)
            is not CpnTokenOccurrenceReconstructionFailure
        ):
            raise TypeError("failure has the wrong type")


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrenceReconstructorIdentity:
    """Identity of deterministic token-occurrence reconstruction."""

    value: str = "projectkoios.workflow.cpn.occurrence-reconstructor:0.1"


@final
class CpnTokenOccurrenceReconstructor:
    """Reconstruct the least feasible occurrences for one value binding."""

    __slots__ = ()

    @property
    def identity(self) -> CpnTokenOccurrenceReconstructorIdentity:
        """Return exact reconstruction semantics identity."""
        return CpnTokenOccurrenceReconstructorIdentity()

    def execute(
        self, request: CpnTokenOccurrenceReconstructionRequest
    ) -> CpnTokenOccurrenceReconstructionResponse:
        """Return a named success or failure response."""
        if type(request) is not CpnTokenOccurrenceReconstructionRequest:
            raise TypeError(
                "request must be CpnTokenOccurrenceReconstructionRequest"
            )
        definition = request.definition
        marking = request.marking
        binding = request.binding
        values = {
            item.variable_identity: item.value for item in binding.assignments
        }
        by_place = {item.place_identity: item.tokens for item in marking.places}
        demands: list[
            tuple[CpnArcDefinition, CpnInputMode, int, CpnTokenPattern]
        ] = []
        candidates: list[tuple[tuple[int, CpnToken], ...]] = []
        inhibitors: list[CpnInhibitorEvaluation] = []
        for arc in definition.arcs:
            if (
                arc.transition_identity != binding.transition_identity
                or arc.input_inscription is None
            ):
                continue
            inscription = arc.input_inscription
            tokens = by_place[arc.place_identity]
            if inscription.mode is CpnInputMode.INHIBIT:
                for index, pattern in enumerate(inscription.patterns):
                    count = sum(
                        token.color_identity in pattern.allowed_color_identities
                        for token in tokens
                    )
                    inhibitors.append(
                        CpnInhibitorEvaluation(
                            arc.identity, arc.place_identity, index, count
                        )
                    )
                    if count:
                        return CpnTokenOccurrenceReconstructionResponse(
                            failure=CpnTokenOccurrenceReconstructionFailure(
                                "an inhibitor pattern matched"
                            )
                        )
                continue
            for index, pattern in enumerate(inscription.patterns):
                assert type(pattern) is CpnTokenPattern
                expected = values[pattern.variable_identity]
                demands.append((arc, inscription.mode, index, pattern))
                candidates.append(
                    tuple(
                        (ordinal, token)
                        for ordinal, token in enumerate(tokens)
                        if token.color_identity
                        in pattern.allowed_color_identities
                        and token.value == expected
                    )
                )
        if any(not items for items in candidates):
            return CpnTokenOccurrenceReconstructionResponse(
                failure=CpnTokenOccurrenceReconstructionFailure(
                    "a demanded token occurrence is unavailable"
                )
            )
        for selected in product(*candidates) if candidates else [()]:
            reserved: set[tuple[object, object, int]] = set()
            consumed: list[CpnTokenOccurrence] = []
            read: list[CpnTokenOccurrence] = []
            feasible = True
            for (arc, mode, index, pattern), selected_token in zip(
                demands, selected, strict=True
            ):
                del pattern
                ordinal, token = selected_token
                coordinate = (arc.place_identity, mode, ordinal)
                if coordinate in reserved:
                    feasible = False
                    break
                reserved.add(coordinate)
                occurrence = CpnTokenOccurrence(
                    arc.identity, arc.place_identity, index, ordinal, token
                )
                if mode is CpnInputMode.CONSUME:
                    consumed.append(occurrence)
                else:
                    read.append(occurrence)
            if feasible:
                return CpnTokenOccurrenceReconstructionResponse(
                    success=CpnTokenOccurrenceReconstructionSuccess(
                        tuple(consumed), tuple(read), tuple(inhibitors)
                    )
                )
        return CpnTokenOccurrenceReconstructionResponse(
            failure=CpnTokenOccurrenceReconstructionFailure(
                "token occurrence reservations conflict"
            )
        )
