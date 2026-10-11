"""Complete deterministic enablement for generic colored Petri nets.

Enablement is a pure ActionObject operation over one exact definition and
marking. Private occurrence coordinates enforce multiset capacity; public
bindings contain only definition-declared variable/value assignments. The
operation performs no selection, firing, Task invocation, external effect,
persistence, authority decision, or scientific calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import product
from string import hexdigits
from typing import final

from .canonical.bindings import (
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingEncodingInput,
)
from .canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from .canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingEncodingInput,
)
from .control.records.ordering import (
    CpnValueOrderingInput,
    CpnValueOrderingPolicy,
)
from .control.records.value_canonical import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from .definitions import (
    CpnDefinition,
    CpnSelectionPolicy,
)
from .expressions.evaluation import (
    CpnExpressionEvaluatorIdentity,
    CpnGuardEvaluationInput,
    CpnGuardEvaluator,
)
from .expressions.grammar import (
    CpnInputMode,
    CpnTokenPattern,
)
from .bindings import CpnBinding, CpnBindingAssignment
from .definitions import CpnDefinitionIdentity
from .markings import CpnMarking, CpnMarkingIdentity
from .validation.definitions import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from .validation.findings import CpnValidationIssue
from .validation.markings import (
    CpnMarkingValidationInput,
    CpnMarkingValidator,
)
from .values import CpnToken, CpnValue


@dataclass(frozen=True, slots=True)
class CpnEnablementResultIdentity:
    """Content identity of one complete enablement operation result.

    ``value`` is the lowercase SHA-256 digest of the enabler-owned canonical
    identity preimage. The digest contract is independent of the deferred public
    result serialization format.
    """

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("enablement result identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "enablement result identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class CpnOrderingPolicyIdentity:
    """Nominal identity of exact enablement ordering semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError("ordering policy identity value must be a string")
        if not self.value:
            raise ValueError("ordering policy identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnTransitionEnablerIdentity:
    """Nominal identity of exact transition-enablement semantics."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact nonempty built-in string."""
        if type(self.value) is not str:
            raise TypeError(
                "transition enabler identity value must be a string"
            )
        if not self.value:
            raise ValueError(
                "transition enabler identity value must not be empty"
            )


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureIdentity:
    """Nominal identity of the failure variant of one enablement result."""

    result_identity: CpnEnablementResultIdentity

    def __post_init__(self) -> None:
        """Bind the failure identity to one exact result identity."""
        if type(self.result_identity) is not CpnEnablementResultIdentity:
            raise TypeError(
                "result_identity must be CpnEnablementResultIdentity"
            )


class CpnEnablementFailureCode(StrEnum):
    """Closed operational failure codes for complete enablement."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_MARKING = "invalid_marking"
    UNSUPPORTED_EXPRESSION_EVALUATOR = "unsupported_expression_evaluator"
    UNSUPPORTED_ORDERING_POLICY = "unsupported_ordering_policy"
    GUARD_EVALUATION_FAILED = "guard_evaluation_failed"


@dataclass(frozen=True, slots=True)
class CpnEnablementFailure:
    """One structured failure with no enabled-binding payload."""

    identity: CpnEnablementFailureIdentity
    code: CpnEnablementFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[CpnValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "software enablement only",
        "no firing or external effect",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable closed failure state."""
        if type(self.identity) is not CpnEnablementFailureIdentity:
            raise TypeError("identity must be CpnEnablementFailureIdentity")
        if not isinstance(self.code, CpnEnablementFailureCode):
            raise TypeError("code must be CpnEnablementFailureCode")
        for name in (
            "operation_phase",
            "expected_condition",
            "observed_condition",
            "diagnostic",
        ):
            value = getattr(self, name)
            if type(value) is not str:
                raise TypeError(f"{name} must be a string")
            if not value:
                raise ValueError(f"{name} must not be empty")
        if type(self.validation_issues) is not tuple or any(
            type(item) is not CpnValidationIssue
            for item in self.validation_issues
        ):
            raise TypeError(
                "validation_issues must be a tuple of CpnValidationIssue"
            )
        if type(self.claim_boundary) is not tuple or any(
            type(item) is not str for item in self.claim_boundary
        ):
            raise TypeError("claim_boundary must be a tuple of strings")
        if not self.claim_boundary or any(
            not item for item in self.claim_boundary
        ):
            raise ValueError("claim_boundary must contain nonempty strings")


@dataclass(frozen=True, slots=True)
class CpnEnablementResult:
    """Closed complete success or failure for one definition and marking."""

    identity: CpnEnablementResultIdentity
    definition_identity: CpnDefinitionIdentity
    selection_policy: CpnSelectionPolicy
    marking_identity: CpnMarkingIdentity
    expression_evaluator_identity: CpnExpressionEvaluatorIdentity
    ordering_policy_identity: CpnOrderingPolicyIdentity
    transition_enabler_identity: CpnTransitionEnablerIdentity
    enabled_bindings: tuple[CpnBinding, ...] | None = None
    failure: CpnEnablementFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal identities and one closed outcome variant."""
        expected = (
            ("identity", CpnEnablementResultIdentity),
            ("definition_identity", CpnDefinitionIdentity),
            ("selection_policy", CpnSelectionPolicy),
            ("marking_identity", CpnMarkingIdentity),
            (
                "expression_evaluator_identity",
                CpnExpressionEvaluatorIdentity,
            ),
            ("ordering_policy_identity", CpnOrderingPolicyIdentity),
            (
                "transition_enabler_identity",
                CpnTransitionEnablerIdentity,
            ),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        if self.enabled_bindings is not None and (
            type(self.enabled_bindings) is not tuple
            or any(
                type(item) is not CpnBinding for item in self.enabled_bindings
            )
        ):
            raise TypeError(
                "enabled_bindings must be a tuple of CpnBinding or None"
            )
        if self.failure is not None and (
            type(self.failure) is not CpnEnablementFailure
        ):
            raise TypeError("failure must be CpnEnablementFailure or None")
        if (self.enabled_bindings is None) == (self.failure is None):
            raise ValueError(
                "exactly one of enabled_bindings and failure must be present"
            )
        if self.enabled_bindings is not None and len(
            set(self.enabled_bindings)
        ) != len(self.enabled_bindings):
            raise ValueError("enabled_bindings must be unique")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")

    @property
    def is_success(self) -> bool:
        """Return whether this closed result contains enabled bindings."""
        return self.enabled_bindings is not None


_EXPRESSION_EVALUATOR_IDENTITY = CpnExpressionEvaluatorIdentity()
_ORDERING_POLICY_IDENTITY = CpnOrderingPolicyIdentity(
    "colored-petri-net-enablement-order-v1"
)
_TRANSITION_ENABLER_IDENTITY = CpnTransitionEnablerIdentity(
    "colored-petri-net-transition-enabler-v1"
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


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureBuildingInput:
    """Complete immutable input for one enablement failure response."""

    definition: CpnDefinition
    marking: CpnMarking
    expression_identity: CpnExpressionEvaluatorIdentity
    ordering_identity: CpnOrderingPolicyIdentity
    enabler_identity: CpnTransitionEnablerIdentity
    failure_state: CpnEnablementFailureState

    def __post_init__(self) -> None:
        expected = (
            ("definition", CpnDefinition),
            ("marking", CpnMarking),
            ("expression_identity", CpnExpressionEvaluatorIdentity),
            ("ordering_identity", CpnOrderingPolicyIdentity),
            ("enabler_identity", CpnTransitionEnablerIdentity),
            ("failure_state", CpnEnablementFailureState),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")


@dataclass(frozen=True, slots=True)
class CpnEnablementFailureBuilderIdentity:
    """Identity of exact enablement-failure construction semantics."""

    value: str = "projectkoios.workflow.cpn.enablement-failure-builder:0.1"


@final
class CpnEnablementFailureBuilder:
    """Construct one identity-bound enablement failure response."""

    __slots__ = ()

    @property
    def identity(self) -> CpnEnablementFailureBuilderIdentity:
        """Return exact failure-construction semantics identity."""
        return CpnEnablementFailureBuilderIdentity()

    def execute(
        self, building_input: CpnEnablementFailureBuildingInput
    ) -> CpnEnablementResult:
        """Return one complete failure result from typed immutable input."""
        if type(building_input) is not CpnEnablementFailureBuildingInput:
            raise TypeError(
                "building_input must be CpnEnablementFailureBuildingInput"
            )
        state = building_input.failure_state
        result_identity = CpnEnablementResultIdentityDeriver().execute(
            CpnEnablementResultIdentityDerivationInput(
                building_input.definition,
                building_input.marking,
                building_input.expression_identity,
                building_input.ordering_identity,
                building_input.enabler_identity,
                None,
                state,
            )
        )
        failure = CpnEnablementFailure(
            CpnEnablementFailureIdentity(result_identity),
            state.code,
            state.operation_phase,
            state.expected_condition,
            state.observed_condition,
            state.diagnostic,
            state.validation_issues,
        )
        return CpnEnablementResult(
            result_identity,
            building_input.definition.identity,
            building_input.definition.selection_policy,
            building_input.marking.identity,
            building_input.expression_identity,
            building_input.ordering_identity,
            building_input.enabler_identity,
            failure=failure,
        )


@dataclass(frozen=True, slots=True)
class CpnEnabledBindingOrderingInput:
    """One exact definition and unique binding set requested for ordering."""

    definition: CpnDefinition
    bindings: frozenset[CpnBinding]

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.bindings) is not frozenset or any(
            type(item) is not CpnBinding for item in self.bindings
        ):
            raise TypeError("bindings must contain exact CpnBinding values")


@dataclass(frozen=True, slots=True)
class CpnEnabledBindingOrderingResult:
    """One deterministically ordered complete binding tuple."""

    bindings: tuple[CpnBinding, ...]

    def __post_init__(self) -> None:
        if type(self.bindings) is not tuple or any(
            type(item) is not CpnBinding for item in self.bindings
        ):
            raise TypeError("bindings must contain exact CpnBinding values")
        if len(set(self.bindings)) != len(self.bindings):
            raise ValueError("bindings must be unique")


@final
class CpnEnabledBindingOrderingPolicy:
    """Order enabled bindings by transition priority and generic values."""

    __slots__ = ()

    @property
    def identity(self) -> CpnOrderingPolicyIdentity:
        """Return exact enabled-binding ordering semantics identity."""
        return _ORDERING_POLICY_IDENTITY

    def execute(
        self, ordering_input: CpnEnabledBindingOrderingInput
    ) -> CpnEnabledBindingOrderingResult:
        """Return all supplied bindings in the exact execution order."""
        if type(ordering_input) is not CpnEnabledBindingOrderingInput:
            raise TypeError(
                "ordering_input must be CpnEnabledBindingOrderingInput"
            )
        priority = {
            identity: position
            for position, identity in enumerate(
                ordering_input.definition.transition_priority
            )
        }
        if any(
            item.transition_identity not in priority
            for item in ordering_input.bindings
        ):
            raise ValueError("binding names an unordered transition")
        ordered: list[tuple[tuple[object, ...], bytes, CpnBinding]] = []
        for binding in ordering_input.bindings:
            key = (
                priority[binding.transition_identity],
                tuple(
                    CpnValueOrderingPolicy()
                    .execute(CpnValueOrderingInput(item.value))
                    .key
                    for item in binding.assignments
                ),
            )
            canonical_bytes = (
                CpnCanonicalBindingCodec()
                .encode(CpnCanonicalBindingEncodingInput(binding))
                .canonical_bytes
            )
            ordered.append((key, canonical_bytes, binding))
        ordered.sort()
        return CpnEnabledBindingOrderingResult(
            tuple(item[2] for item in ordered)
        )


@dataclass(frozen=True, slots=True)
class CpnTransitionEnablementRequest:
    """Complete immutable request for deterministic transition enablement."""

    definition: CpnDefinition
    marking: CpnMarking
    expression_evaluator_identity: CpnExpressionEvaluatorIdentity = (
        _EXPRESSION_EVALUATOR_IDENTITY
    )
    ordering_policy_identity: CpnOrderingPolicyIdentity = (
        _ORDERING_POLICY_IDENTITY
    )

    def __post_init__(self) -> None:
        expected = (
            ("definition", CpnDefinition),
            ("marking", CpnMarking),
            ("expression_evaluator_identity", CpnExpressionEvaluatorIdentity),
            ("ordering_policy_identity", CpnOrderingPolicyIdentity),
        )
        for name, nominal_type in expected:
            if type(getattr(self, name)) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")


@final
class CpnTransitionEnabler:
    """ActionObject enumerating the complete enabled transition/binding set."""

    __slots__ = ()

    @property
    def identity(self) -> CpnTransitionEnablerIdentity:
        """Return exact complete-enablement semantics identity."""
        return _TRANSITION_ENABLER_IDENTITY

    def execute(
        self, request: CpnTransitionEnablementRequest
    ) -> CpnEnablementResult:
        """Return complete deterministic enablement or one structured failure.

        Wrong public argument types raise ``TypeError``. Cross-object defects,
        unsupported semantic versions, and guard failures are represented by the
        returned closed failure variant.
        """
        if type(request) is not CpnTransitionEnablementRequest:
            raise TypeError("request must be CpnTransitionEnablementRequest")
        definition = request.definition
        marking = request.marking
        expression_evaluator_identity = request.expression_evaluator_identity
        ordering_policy_identity = request.ordering_policy_identity
        common = (
            definition,
            marking,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
        )
        failure_builder = CpnEnablementFailureBuilder()
        definition_validation = CpnDefinitionValidator().execute(
            CpnDefinitionValidationRequest(definition)
        )
        if not definition_validation.is_valid:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.INVALID_DEFINITION,
                        "definition_validation",
                        "a structurally valid colored Petri-net definition",
                        "definition validation returned findings",
                        "enablement was not evaluated",
                        definition_validation.issues,
                    ),
                )
            )
        marking_validation = CpnMarkingValidator().execute(
            CpnMarkingValidationInput(definition, marking)
        )
        if not marking_validation.is_valid:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.INVALID_MARKING,
                        "marking_validation",
                        "a complete marking compatible with the exact definition",
                        "marking validation returned findings",
                        "enablement was not evaluated",
                        marking_validation.issues,
                    ),
                )
            )
        if expression_evaluator_identity != _EXPRESSION_EVALUATOR_IDENTITY:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.UNSUPPORTED_EXPRESSION_EVALUATOR,
                        "expression_evaluator_resolution",
                        _EXPRESSION_EVALUATOR_IDENTITY.value,
                        expression_evaluator_identity.value,
                        "enablement was not evaluated under an unsupported semantic version",
                    ),
                )
            )
        if ordering_policy_identity != _ORDERING_POLICY_IDENTITY:
            return failure_builder.execute(
                CpnEnablementFailureBuildingInput(
                    *common,
                    CpnEnablementFailureState(
                        CpnEnablementFailureCode.UNSUPPORTED_ORDERING_POLICY,
                        "ordering_policy_resolution",
                        _ORDERING_POLICY_IDENTITY.value,
                        ordering_policy_identity.value,
                        "enablement was not evaluated under an unsupported semantic version",
                    ),
                )
            )

        enabled: set[CpnBinding] = set()
        by_place = {
            place.place_identity: place.tokens for place in marking.places
        }
        guard_evaluator = CpnGuardEvaluator()
        for transition in definition.transitions:
            arcs = tuple(
                arc
                for arc in definition.arcs
                if arc.transition_identity == transition.identity
                and arc.input_inscription is not None
            )
            inhibited = False
            demands: list[
                tuple[
                    object,
                    CpnInputMode,
                    CpnTokenPattern,
                ]
            ] = []
            candidates: list[tuple[tuple[int, CpnToken], ...]] = []
            for arc in arcs:
                inscription = arc.input_inscription
                assert inscription is not None
                tokens = by_place[arc.place_identity]
                if inscription.mode is CpnInputMode.INHIBIT:
                    for pattern in inscription.patterns:
                        if any(
                            token.color_identity
                            in pattern.allowed_color_identities
                            for token in tokens
                        ):
                            inhibited = True
                            break
                    if inhibited:
                        break
                    continue
                for pattern in inscription.patterns:
                    assert type(pattern) is CpnTokenPattern
                    demands.append(
                        (arc.place_identity, inscription.mode, pattern)
                    )
                    candidates.append(
                        tuple(
                            (index, token)
                            for index, token in enumerate(tokens)
                            if token.color_identity
                            in pattern.allowed_color_identities
                        )
                    )
            if inhibited or any(not items for items in candidates):
                continue
            choices = product(*candidates) if candidates else [()]
            for selected in choices:
                reserved: set[tuple[object, CpnInputMode, int]] = set()
                feasible = True
                values: dict[object, CpnValue] = {}
                for (place, mode, pattern), (index, token) in zip(
                    demands, selected, strict=True
                ):
                    key = (place, mode, index)
                    if key in reserved:
                        feasible = False
                        break
                    reserved.add(key)
                    values[pattern.variable_identity] = token.value
                if not feasible:
                    continue
                binding = CpnBinding(
                    transition.identity,
                    tuple(
                        CpnBindingAssignment(variable, values[variable])
                        for variable in transition.input_variable_identities
                    ),
                )
                try:
                    guard_value = guard_evaluator.execute(
                        CpnGuardEvaluationInput(
                            transition.guard,
                            binding,
                            definition.control_record_types,
                        )
                    ).value
                except (KeyError, TypeError, ValueError) as exc:
                    return failure_builder.execute(
                        CpnEnablementFailureBuildingInput(
                            *common,
                            CpnEnablementFailureState(
                                CpnEnablementFailureCode.GUARD_EVALUATION_FAILED,
                                "guard_evaluation",
                                "a total well-typed guard for every feasible binding",
                                f"guard failed for transition {transition.identity.value}",
                                f"{type(exc).__name__}: {exc}",
                            ),
                        )
                    )
                if guard_value:
                    enabled.add(binding)
        ordered = (
            CpnEnabledBindingOrderingPolicy()
            .execute(
                CpnEnabledBindingOrderingInput(definition, frozenset(enabled))
            )
            .bindings
        )
        identity = CpnEnablementResultIdentityDeriver().execute(
            CpnEnablementResultIdentityDerivationInput(*common, ordered, None)
        )
        return CpnEnablementResult(
            identity,
            definition.identity,
            definition.selection_policy,
            marking.identity,
            expression_evaluator_identity,
            ordering_policy_identity,
            _TRANSITION_ENABLER_IDENTITY,
            enabled_bindings=ordered,
        )
