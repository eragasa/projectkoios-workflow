"""Immutable contracts for retained shadow-firing replay."""

from dataclasses import dataclass

from ..contracts import (
    CpnShadowFiringErrorCode,
    CpnShadowFiringInput,
    CpnShadowFiringResult,
)


@dataclass(frozen=True, slots=True)
class CpnShadowFiringReplayerIdentity:
    """Identity of exact retained shadow-result replay comparison."""

    value: str = "projectkoios.workflow.cpn.shadow-firing-replayer:0.1"


@dataclass(frozen=True, slots=True)
class CpnShadowFiringReplayInput:
    """One original shadow input and one retained result to replay."""

    firing_input: CpnShadowFiringInput
    retained_result: CpnShadowFiringResult

    def __post_init__(self) -> None:
        if type(self.firing_input) is not CpnShadowFiringInput:
            raise TypeError("firing_input must be CpnShadowFiringInput")
        if type(self.retained_result) is not CpnShadowFiringResult:
            raise TypeError("retained_result must be CpnShadowFiringResult")


@dataclass(frozen=True, slots=True)
class CpnShadowFiringReplayResult:
    """Closed exact-match or mismatch replay outcome."""

    is_match: bool
    replayed_result: CpnShadowFiringResult | None
    issue_code: CpnShadowFiringErrorCode | None

    def __post_init__(self) -> None:
        if type(self.is_match) is not bool:
            raise TypeError("is_match must be bool")
        if self.replayed_result is not None and type(
            self.replayed_result
        ) is not (CpnShadowFiringResult):
            raise TypeError(
                "replayed_result must be CpnShadowFiringResult or None"
            )
        if self.issue_code is not None and not isinstance(
            self.issue_code, CpnShadowFiringErrorCode
        ):
            raise TypeError(
                "issue_code must be CpnShadowFiringErrorCode or None"
            )
        if self.is_match:
            if self.replayed_result is None or self.issue_code is not None:
                raise ValueError(
                    "matching replay must contain only a replayed result"
                )
        elif self.issue_code is None:
            raise ValueError("mismatching replay must contain an issue code")
