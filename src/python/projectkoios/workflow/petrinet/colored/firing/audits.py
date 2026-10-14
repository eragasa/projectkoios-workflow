"""Immutable occurrence and output audit vocabulary for pure firing."""

from __future__ import annotations
from dataclasses import dataclass
from ..definitions import CpnArcIdentity
from ..definitions import CpnPlaceIdentity
from ..values import CpnToken


@dataclass(frozen=True, slots=True)
class CpnTransitionFirerIdentity:
    """Nominal identity of exact pure-firing semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("transition firer identity value must be a string")
        if not self.value:
            raise ValueError(
                "transition firer identity value must not be empty"
            )


@dataclass(frozen=True, slots=True)
class CpnTokenOccurrence:
    """One exact predecessor token occurrence used by an input inscription."""

    arc_identity: CpnArcIdentity
    place_identity: CpnPlaceIdentity
    pattern_index: int
    occurrence_ordinal: int
    token: CpnToken

    def __post_init__(self) -> None:
        """Validate exact nominal occurrence coordinates."""
        expected = (
            (self.arc_identity, CpnArcIdentity, "arc_identity"),
            (
                self.place_identity,
                CpnPlaceIdentity,
                "place_identity",
            ),
            (self.token, CpnToken, "token"),
        )
        for value, nominal_type, name in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        for name in ("pattern_index", "occurrence_ordinal"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


@dataclass(frozen=True, slots=True)
class CpnInhibitorEvaluation:
    """One audited nonbinding inhibitor absence evaluation."""

    arc_identity: CpnArcIdentity
    place_identity: CpnPlaceIdentity
    pattern_index: int
    matching_count: int

    def __post_init__(self) -> None:
        """Validate exact nonnegative inhibitor audit coordinates."""
        if type(self.arc_identity) is not CpnArcIdentity:
            raise TypeError("arc_identity must be CpnArcIdentity")
        if type(self.place_identity) is not CpnPlaceIdentity:
            raise TypeError("place_identity must be CpnPlaceIdentity")
        for name in ("pattern_index", "matching_count"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


@dataclass(frozen=True, slots=True)
class CpnProducedToken:
    """One exact produced token and destination output coordinate."""

    arc_identity: CpnArcIdentity
    place_identity: CpnPlaceIdentity
    template_index: int
    token: CpnToken

    def __post_init__(self) -> None:
        """Validate exact produced-token audit state."""
        if type(self.arc_identity) is not CpnArcIdentity:
            raise TypeError("arc_identity must be CpnArcIdentity")
        if type(self.place_identity) is not CpnPlaceIdentity:
            raise TypeError("place_identity must be CpnPlaceIdentity")
        if type(self.template_index) is not int:
            raise TypeError("template_index must be an integer")
        if self.template_index < 0:
            raise ValueError("template_index must be nonnegative")
        if type(self.token) is not CpnToken:
            raise TypeError("token must be CpnToken")


@dataclass(frozen=True, slots=True)
class CpnFiringAudit:
    """Complete immutable occurrence and output audit for successful firing."""

    consumed_occurrences: tuple[CpnTokenOccurrence, ...]
    read_occurrences: tuple[CpnTokenOccurrence, ...]
    inhibitor_evaluations: tuple[CpnInhibitorEvaluation, ...]
    produced_tokens: tuple[CpnProducedToken, ...]
    firer_identity: CpnTransitionFirerIdentity

    def __post_init__(self) -> None:
        """Validate exact immutable audit collections."""
        collections = (
            ("consumed_occurrences", CpnTokenOccurrence),
            ("read_occurrences", CpnTokenOccurrence),
            ("inhibitor_evaluations", CpnInhibitorEvaluation),
            ("produced_tokens", CpnProducedToken),
        )
        for name, member_type in collections:
            values = getattr(self, name)
            if type(values) is not tuple or any(
                type(item) is not member_type for item in values
            ):
                raise TypeError(
                    f"{name} must be a tuple of {member_type.__name__}"
                )
        if type(self.firer_identity) is not CpnTransitionFirerIdentity:
            raise TypeError("firer_identity must be CpnTransitionFirerIdentity")
