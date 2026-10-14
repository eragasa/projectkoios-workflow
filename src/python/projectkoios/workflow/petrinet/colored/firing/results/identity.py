"""Content identity derivation for complete firing outcomes."""

from __future__ import annotations
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final
from ...canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from ...canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingEncodingInput,
)
from ...control.records.values.canonicalization import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ...markings import CpnMarking
from ...validation.findings import CpnValidationIssue
from ..audits import CpnFiringAudit, CpnTransitionFirerIdentity
from ..inputs import CpnFiringInput
from .definition import CpnFiringFailureCode, CpnFiringResultIdentity


@dataclass(frozen=True, slots=True)
class CpnFiringFailureState:
    """Immutable failure data before result identity construction."""

    code: CpnFiringFailureCode
    phase: str
    expected: str
    observed: str
    issues: tuple[CpnValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class CpnFiringResultIdentityDerivationRequest:
    """Complete firing input and exactly one represented outcome."""

    firing_input: CpnFiringInput
    successor: CpnMarking | None = None
    audit: CpnFiringAudit | None = None
    failure: CpnFiringFailureState | None = None

    def __post_init__(self) -> None:
        if type(self.firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        success = (
            type(self.successor) is CpnMarking
            and type(self.audit) is CpnFiringAudit
            and self.failure is None
        )
        failed = (
            self.successor is None
            and self.audit is None
            and type(self.failure) is CpnFiringFailureState
        )
        if not (success or failed):
            raise ValueError("exactly one complete firing outcome is required")


@dataclass(frozen=True, slots=True)
class CpnFiringResultIdentityDeriverIdentity:
    """Identity of exact firing-result identity derivation."""

    value: str = "projectkoios.workflow.cpn.firing-result-identity-deriver:0.1"


@final
class CpnFiringResultIdentityDeriver:
    """Derive a firing identity from typed immutable represented state."""

    __slots__ = ()

    @property
    def identity(self) -> CpnFiringResultIdentityDeriverIdentity:
        """Return exact identity-derivation semantics identity."""
        return CpnFiringResultIdentityDeriverIdentity()

    def execute(
        self, request: CpnFiringResultIdentityDerivationRequest
    ) -> CpnFiringResultIdentity:
        """Return the content identity for exactly one represented outcome."""
        if type(request) is not CpnFiringResultIdentityDerivationRequest:
            raise TypeError(
                "request must be CpnFiringResultIdentityDerivationRequest"
            )
        firing_input = request.firing_input
        definition_document = CpnCanonicalDefinitionCodec().encode(
            CpnCanonicalDefinitionEncodingInput(firing_input.definition)
        )
        predecessor_document = CpnCanonicalMarkingCodec().encode(
            CpnCanonicalMarkingEncodingInput(firing_input.predecessor_marking)
        )
        binding_states = []
        for binding in (
            firing_input.selected_binding,
            firing_input.external_output_binding,
        ):
            binding_states.append(
                {
                    "transition": binding.transition_identity.value,
                    "assignments": [
                        {
                            "variable": item.variable_identity.value,
                            "kind": item.value.kind.value,
                            "value": json.loads(
                                CpnValueCanonicalizer()
                                .execute(
                                    CpnValueCanonicalizationInput(item.value)
                                )
                                .canonical_bytes
                            ),
                        }
                        for item in binding.assignments
                    ],
                }
            )
        represented_outcome: dict[str, object]
        if request.failure is not None:
            failure = request.failure
            represented_outcome = {
                "kind": "failure",
                "code": failure.code.value,
                "phase": failure.phase,
                "expected": failure.expected,
                "observed": failure.observed,
                "issues": [
                    {
                        "path": list(item.path),
                        "code": item.code.value,
                        "related": list(item.related_identities),
                        "message": item.message,
                    }
                    for item in failure.issues
                ],
            }
        else:
            assert request.successor is not None and request.audit is not None
            represented_outcome = {
                "kind": "success",
                "successor": request.successor.identity.value,
                "consumed": [
                    {
                        "arc": item.arc_identity.value,
                        "place": item.place_identity.value,
                        "pattern": item.pattern_index,
                        "ordinal": item.occurrence_ordinal,
                        "token_identity": None
                        if item.token.token_identity is None
                        else item.token.token_identity.value,
                    }
                    for item in request.audit.consumed_occurrences
                ],
                "read": [
                    {
                        "arc": item.arc_identity.value,
                        "place": item.place_identity.value,
                        "pattern": item.pattern_index,
                        "ordinal": item.occurrence_ordinal,
                        "token_identity": None
                        if item.token.token_identity is None
                        else item.token.token_identity.value,
                    }
                    for item in request.audit.read_occurrences
                ],
                "produced": [
                    {
                        "arc": item.arc_identity.value,
                        "place": item.place_identity.value,
                        "index": item.template_index,
                        "token_identity": None
                        if item.token.token_identity is None
                        else item.token.token_identity.value,
                    }
                    for item in request.audit.produced_tokens
                ],
            }
        encoded = json.dumps(
            {
                "domain": "projectkoios.workflow.cpn.firing-result:0.1",
                "definition_canonical_bytes_hex": (
                    definition_document.canonical_bytes.hex()
                ),
                "predecessor_canonical_bytes_hex": (
                    predecessor_document.canonical_bytes.hex()
                ),
                "enablement": firing_input.enablement_result.identity.value,
                "selection": firing_input.selection_result.identity.value,
                "transition": firing_input.transition_identity.value,
                "selected_binding": binding_states[0],
                "external_output_binding": binding_states[1],
                "directive": None
                if firing_input.directive_identity is None
                else firing_input.directive_identity.value,
                "outcome": represented_outcome,
                "firer": CpnTransitionFirerIdentity(
                    "projectkoios.workflow.cpn.transition-firer:0.1"
                ).value,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return CpnFiringResultIdentity(sha256(encoded).hexdigest())
