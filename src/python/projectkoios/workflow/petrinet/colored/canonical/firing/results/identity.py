"""Canonical firing-result codec identity required by profile resolution."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultCodecIdentity:
    """Identity of exact canonical firing-result replay transport."""

    value: str = "projectkoios.workflow.cpn.canonical-firing-result-codec:0.1"
