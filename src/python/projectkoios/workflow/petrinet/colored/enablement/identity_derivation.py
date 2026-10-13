"""Content identity derivation for complete enablement outcomes."""

from __future__ import annotations
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final
from ..canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from ..canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingEncodingInput,
)
from ..control.records.value_canonical import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ..definitions import CpnDefinition
from ..expressions.evaluation import CpnExpressionEvaluatorIdentity
from ..bindings import CpnBinding
from ..markings import CpnMarking
from ..validation.findings import CpnValidationIssue
from .outcomes import (
    CpnEnablementFailureCode,
    CpnEnablementResultIdentity,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablerIdentity,
)


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureState:
    """Exact prospective failure state used by result identity derivation."""

    code: CpnEnablementFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[CpnValidationIssue, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.code, CpnEnablementFailureCode):
            raise TypeError("code must be CpnEnablementFailureCode")
        for name in (
            "operation_phase",
            "expected_condition",
            "observed_condition",
            "diagnostic",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if type(self.validation_issues) is not tuple or any(
            type(item) is not CpnValidationIssue
            for item in self.validation_issues
        ):
            raise TypeError(
                "validation_issues must be a tuple of CpnValidationIssue"
            )


@dataclass(frozen=True, slots=True)
class CpnEnablementResultIdentityDeriverIdentity:
    """Identity of exact enablement-result identity derivation semantics."""

    value: str = (
        "projectkoios.workflow.cpn.enablement-result-identity-deriver:0.1"
    )


@dataclass(frozen=True, slots=True)
class CpnEnablementResultIdentityDerivationInput:
    """Complete typed input to one enablement-result identity derivation."""

    definition: CpnDefinition
    marking: CpnMarking
    expression_identity: CpnExpressionEvaluatorIdentity
    ordering_identity: CpnOrderingPolicyIdentity
    enabler_identity: CpnTransitionEnablerIdentity
    bindings: tuple[CpnBinding, ...] | None
    failure: CpnEnablementFailureState | None

    def __post_init__(self) -> None:
        expected = (
            ("definition", CpnDefinition),
            ("marking", CpnMarking),
            ("expression_identity", CpnExpressionEvaluatorIdentity),
            ("ordering_identity", CpnOrderingPolicyIdentity),
            ("enabler_identity", CpnTransitionEnablerIdentity),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.bindings is not None and (
            type(self.bindings) is not tuple
            or any(type(item) is not CpnBinding for item in self.bindings)
        ):
            raise TypeError("bindings must be a tuple of CpnBinding or None")
        if (
            self.failure is not None
            and type(self.failure) is not CpnEnablementFailureState
        ):
            raise TypeError("failure must be CpnEnablementFailureState or None")
        if (self.bindings is None) == (self.failure is None):
            raise ValueError("exactly one of bindings and failure is required")


@final
class CpnEnablementResultIdentityDeriver:
    """Derive an identity over exact represented input and closed outcome state."""

    __slots__ = ()

    @property
    def identity(self) -> CpnEnablementResultIdentityDeriverIdentity:
        """Return exact enablement identity-derivation semantics."""
        return CpnEnablementResultIdentityDeriverIdentity()

    def execute(
        self, derivation_input: CpnEnablementResultIdentityDerivationInput
    ) -> CpnEnablementResultIdentity:
        """Encode exact typed inputs without accepting an arbitrary root object."""
        if (
            type(derivation_input)
            is not CpnEnablementResultIdentityDerivationInput
        ):
            raise TypeError(
                "derivation_input must be "
                "CpnEnablementResultIdentityDerivationInput"
            )

        definition_document = CpnCanonicalDefinitionCodec().encode(
            CpnCanonicalDefinitionEncodingInput(derivation_input.definition)
        )
        marking_document = CpnCanonicalMarkingCodec().encode(
            CpnCanonicalMarkingEncodingInput(derivation_input.marking)
        )
        bindings = derivation_input.bindings
        encoded_bindings = None
        if bindings is not None:
            encoded_bindings = [
                {
                    "transition": binding.transition_identity.value,
                    "assignments": [
                        {
                            "variable": assignment.variable_identity.value,
                            "kind": assignment.value.kind.value,
                            "value": json.loads(
                                CpnValueCanonicalizer()
                                .execute(
                                    CpnValueCanonicalizationInput(
                                        assignment.value
                                    )
                                )
                                .canonical_bytes
                            ),
                        }
                        for assignment in binding.assignments
                    ],
                }
                for binding in bindings
            ]
        failure = derivation_input.failure
        encoded_failure = None
        if failure is not None:
            encoded_failure = {
                "code": failure.code.value,
                "operation_phase": failure.operation_phase,
                "expected_condition": failure.expected_condition,
                "observed_condition": failure.observed_condition,
                "diagnostic": failure.diagnostic,
                "validation_issues": [
                    {
                        "code": item.code.value,
                        "message": item.message,
                        "path": list(item.path),
                        "related_identities": list(item.related_identities),
                    }
                    for item in failure.validation_issues
                ],
            }
        payload = {
            "domain": "projectkoios.workflow.cpn.enablement-result:0.1",
            "definition_canonical_bytes_hex": (
                definition_document.canonical_bytes.hex()
            ),
            "selection_policy": derivation_input.definition.selection_policy.value,
            "marking_canonical_bytes_hex": marking_document.canonical_bytes.hex(),
            "expression": derivation_input.expression_identity.value,
            "ordering": derivation_input.ordering_identity.value,
            "enabler": derivation_input.enabler_identity.value,
            "bindings": encoded_bindings,
            "failure": encoded_failure,
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return CpnEnablementResultIdentity(sha256(encoded).hexdigest())
