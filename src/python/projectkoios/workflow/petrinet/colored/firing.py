"""Identity-closed pure firing for generic colored Petri nets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import product
from string import hexdigits
from typing import final

from .canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from .canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingEncodingInput,
)
from .control.records.value_canonical import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from .definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnDefinition,
)
from .enablement import (
    CpnEnablementResult,
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from .expressions.evaluation import (
    CpnExpressionEvaluationInput,
    CpnExpressionEvaluator,
)
from .expressions.grammar import (
    CpnInputMode,
    CpnTokenPattern,
)
from .external_outputs import (
    CpnExternalOutputValidationInput,
    CpnExternalOutputValidator,
)
from .bindings import CpnBinding
from .definitions import CpnPlaceIdentity, CpnTransitionIdentity
from .markings import CpnMarking, CpnMarkingIdentity, CpnPlaceMarking
from .selection import (
    CpnBindingSelectionRequest,
    CpnBindingSelector,
    CpnSelectionDirectiveIdentity,
    CpnSelectionOutcomeKind,
    CpnSelectionResult,
)
from .validation.definitions import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from .validation.findings import CpnValidationIssue
from .validation.markings import (
    CpnMarkingValidationInput,
    CpnMarkingValidator,
)
from .values import (
    CpnToken,
    CpnTokenIdentity,
    CpnValueKind,
)


@dataclass(frozen=True, slots=True)
class CpnFiringResultIdentity:
    """Content identity of one closed firing result."""

    value: str

    def __post_init__(self) -> None:
        """Require one exact lowercase SHA-256 spelling."""
        if type(self.value) is not str:
            raise TypeError("firing result identity value must be a string")
        if (
            len(self.value) != 64
            or self.value != self.value.lower()
            or any(character not in hexdigits for character in self.value)
        ):
            raise ValueError(
                "firing result identity must be a lowercase SHA-256 digest"
            )


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


class CpnFiringFailureCode(StrEnum):
    """Closed pure-firing failure codes."""

    INVALID_DEFINITION = "invalid_definition"
    INVALID_PREDECESSOR_MARKING = "invalid_predecessor_marking"
    ENABLEMENT_MISMATCH = "enablement_mismatch"
    SELECTION_MISMATCH = "selection_mismatch"
    DIRECTIVE_MISMATCH = "directive_mismatch"
    TRANSITION_OR_BINDING_MISMATCH = "transition_or_binding_mismatch"
    EXTERNAL_OUTPUT_BINDING_MISMATCH = "external_output_binding_mismatch"
    INPUT_OCCURRENCE_RECONSTRUCTION_FAILED = (
        "input_occurrence_reconstruction_failed"
    )
    OUTPUT_EVALUATION_FAILED = "output_evaluation_failed"
    PRODUCED_TOKEN_INVALID = "produced_token_invalid"
    TOKEN_IDENTITY_COLLISION = "token_identity_collision"


@dataclass(frozen=True, slots=True)
class CpnFiringFailureIdentity:
    """Nominal identity of the failure variant of one firing result."""

    result_identity: CpnFiringResultIdentity

    def __post_init__(self) -> None:
        """Bind to one exact firing-result identity."""
        if type(self.result_identity) is not CpnFiringResultIdentity:
            raise TypeError("result_identity must be CpnFiringResultIdentity")


@dataclass(frozen=True, slots=True)
class CpnFiringFailure:
    """Structured pure-firing failure with no successor."""

    identity: CpnFiringFailureIdentity
    code: CpnFiringFailureCode
    operation_phase: str
    expected_condition: str
    observed_condition: str
    diagnostic: str
    validation_issues: tuple[CpnValidationIssue, ...] = ()
    claim_boundary: tuple[str, ...] = (
        "pure generic firing only",
        "no external effect or authority",
        "no scientific acceptance",
    )

    def __post_init__(self) -> None:
        """Validate immutable structured failure state."""
        if type(self.identity) is not CpnFiringFailureIdentity:
            raise TypeError("identity must be CpnFiringFailureIdentity")
        if not isinstance(self.code, CpnFiringFailureCode):
            raise TypeError("code must be CpnFiringFailureCode")
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


class CpnFiringOutcomeKind(StrEnum):
    """Closed success or failure firing outcome."""

    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class CpnFiringResult:
    """One identity-bound pure-firing success or failure."""

    identity: CpnFiringResultIdentity
    firing_input: CpnFiringInput
    outcome: CpnFiringOutcomeKind
    successor_marking: CpnMarking | None = None
    audit: CpnFiringAudit | None = None
    failure: CpnFiringFailure | None = None

    def __post_init__(self) -> None:
        """Enforce exact nominal types and one closed outcome."""
        if type(self.identity) is not CpnFiringResultIdentity:
            raise TypeError("identity must be CpnFiringResultIdentity")
        if type(self.firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        if not isinstance(self.outcome, CpnFiringOutcomeKind):
            raise TypeError("outcome must be CpnFiringOutcomeKind")
        valid = (
            self.outcome is CpnFiringOutcomeKind.SUCCESS
            and type(self.successor_marking) is CpnMarking
            and type(self.audit) is CpnFiringAudit
            and self.failure is None
        ) or (
            self.outcome is CpnFiringOutcomeKind.FAILURE
            and self.successor_marking is None
            and self.audit is None
            and type(self.failure) is CpnFiringFailure
        )
        if not valid:
            raise ValueError("firing fields do not match the outcome variant")
        if self.failure is not None and (
            self.failure.identity.result_identity != self.identity
        ):
            raise ValueError("failure identity must bind this result identity")


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
                "firer": _FIRER_IDENTITY.value,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return CpnFiringResultIdentity(sha256(encoded).hexdigest())


@dataclass(frozen=True, slots=True)
class CpnSuccessorMarkingBuildingRequest:
    """One firing input and complete audit requested as a successor marking."""

    firing_input: CpnFiringInput
    audit: CpnFiringAudit

    def __post_init__(self) -> None:
        if type(self.firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        if type(self.audit) is not CpnFiringAudit:
            raise TypeError("audit must be CpnFiringAudit")


@dataclass(frozen=True, slots=True)
class CpnSuccessorMarkingBuilderIdentity:
    """Identity of exact successor-marking construction semantics."""

    value: str = "projectkoios.workflow.cpn.successor-marking-builder:0.1"


@final
class CpnSuccessorMarkingBuilder:
    """Construct one content-identified successor from retained firing evidence."""

    __slots__ = ()

    @property
    def identity(self) -> CpnSuccessorMarkingBuilderIdentity:
        """Return exact successor-building semantics identity."""
        return CpnSuccessorMarkingBuilderIdentity()

    def execute(
        self, request: CpnSuccessorMarkingBuildingRequest
    ) -> CpnMarking:
        """Return the exact successor marking represented by the audit."""
        if type(request) is not CpnSuccessorMarkingBuildingRequest:
            raise TypeError(
                "request must be CpnSuccessorMarkingBuildingRequest"
            )
        firing_input = request.firing_input
        audit = request.audit
        consumed = {
            (item.place_identity, item.occurrence_ordinal)
            for item in audit.consumed_occurrences
        }
        produced_by_place: dict[CpnPlaceIdentity, list[CpnToken]] = {}
        for item in audit.produced_tokens:
            produced_by_place.setdefault(item.place_identity, []).append(
                item.token
            )
        places = tuple(
            CpnPlaceMarking(
                place.place_identity,
                tuple(
                    token
                    for ordinal, token in enumerate(place.tokens)
                    if (place.place_identity, ordinal) not in consumed
                )
                + tuple(produced_by_place.get(place.place_identity, ())),
            )
            for place in firing_input.predecessor_marking.places
        )
        represented_places = []
        for place in places:
            represented_tokens = []
            for token in place.tokens:
                represented_tokens.append(
                    {
                        "color": token.color_identity.value,
                        "kind": token.value.kind.value,
                        "value": json.loads(
                            CpnValueCanonicalizer()
                            .execute(CpnValueCanonicalizationInput(token.value))
                            .canonical_bytes
                        ),
                        "identity": (
                            None
                            if token.token_identity is None
                            else token.token_identity.value
                        ),
                    }
                )
            represented_places.append(
                {
                    "place": place.place_identity.value,
                    "tokens": represented_tokens,
                }
            )
        encoded = json.dumps(
            {
                "domain": "projectkoios.workflow.cpn.successor-marking:0.1",
                "definition": firing_input.definition.identity.value,
                "predecessor": firing_input.predecessor_marking.identity.value,
                "places": represented_places,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return CpnMarking(
            CpnMarkingIdentity(sha256(encoded).hexdigest()),
            firing_input.definition.identity,
            places,
        )


@dataclass(frozen=True, slots=True)
class CpnFiringFailureBuildingRequest:
    """One firing input and structured failure state."""

    firing_input: CpnFiringInput
    failure: CpnFiringFailureState


@dataclass(frozen=True, slots=True)
class CpnFiringFailureBuilderIdentity:
    """Identity of exact firing-failure construction semantics."""

    value: str = "projectkoios.workflow.cpn.firing-failure-builder:0.1"


@final
class CpnFiringFailureBuilder:
    """Construct one complete identity-bound firing failure response."""

    __slots__ = ()

    @property
    def identity(self) -> CpnFiringFailureBuilderIdentity:
        """Return exact failure-building semantics identity."""
        return CpnFiringFailureBuilderIdentity()

    def execute(
        self, request: CpnFiringFailureBuildingRequest
    ) -> CpnFiringResult:
        """Return one complete firing failure."""
        if type(request) is not CpnFiringFailureBuildingRequest:
            raise TypeError("request must be CpnFiringFailureBuildingRequest")
        state = request.failure
        identity = CpnFiringResultIdentityDeriver().execute(
            CpnFiringResultIdentityDerivationRequest(
                request.firing_input, failure=state
            )
        )
        failure = CpnFiringFailure(
            CpnFiringFailureIdentity(identity),
            state.code,
            state.phase,
            state.expected,
            state.observed,
            "firing produced no successor",
            state.issues,
        )
        return CpnFiringResult(
            identity,
            request.firing_input,
            CpnFiringOutcomeKind.FAILURE,
            failure=failure,
        )


_FIRER_IDENTITY = CpnTransitionFirerIdentity(
    "projectkoios.workflow.cpn.transition-firer:0.1"
)


@final
@dataclass(frozen=True, slots=True)
class CpnTransitionFirer:
    """Stateless action producing one pure identity-closed successor marking."""

    @property
    def identity(self) -> CpnTransitionFirerIdentity:
        """Return the identity of the compiled firing semantics."""
        return _FIRER_IDENTITY

    def execute(self, firing_input: CpnFiringInput) -> CpnFiringResult:
        """Validate the complete derivation and return success or structured failure."""
        if type(firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        definition = firing_input.definition
        marking = firing_input.predecessor_marking
        definition_validation = CpnDefinitionValidator().execute(
            CpnDefinitionValidationRequest(definition)
        )
        if not definition_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INVALID_DEFINITION,
                        "definition_validation",
                        "a structurally valid definition",
                        "definition validation returned findings",
                        definition_validation.issues,
                    ),
                )
            )
        marking_validation = CpnMarkingValidator().execute(
            CpnMarkingValidationInput(definition, marking)
        )
        if not marking_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INVALID_PREDECESSOR_MARKING,
                        "marking_validation",
                        "a compatible complete predecessor marking",
                        "marking validation returned findings",
                        marking_validation.issues,
                    ),
                )
            )
        recomputed_enablement = CpnTransitionEnabler().execute(
            CpnTransitionEnablementRequest(definition, marking)
        )
        if recomputed_enablement != firing_input.enablement_result:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.ENABLEMENT_MISMATCH,
                        "enablement_replay",
                        "replay-equal complete enablement",
                        "supplied enablement differs from recomputation",
                    ),
                )
            )
        directive = firing_input.selection_result.directive
        recomputed_selection = CpnBindingSelector().execute(
            CpnBindingSelectionRequest(
                definition, recomputed_enablement, directive
            )
        )
        if recomputed_selection != firing_input.selection_result:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.SELECTION_MISMATCH,
                        "selection_replay",
                        "replay-equal exact selection",
                        "supplied selection differs from recomputation",
                    ),
                )
            )
        if (
            firing_input.selection_result.outcome
            is not (CpnSelectionOutcomeKind.SELECTED)
            or firing_input.selection_result.selected_binding
            != firing_input.selected_binding
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                        "selected_binding_validation",
                        "one exact selected binding",
                        "firing binding is not the selected binding",
                    ),
                )
            )
        if (
            firing_input.directive_identity
            != firing_input.selection_result.directive_identity
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.DIRECTIVE_MISMATCH,
                        "directive_validation",
                        "the exact selection directive identity or absence",
                        "firing directive identity differs from selection",
                    ),
                )
            )
        binding = firing_input.selected_binding
        transition = next(
            (
                item
                for item in definition.transitions
                if item.identity == binding.transition_identity
            ),
            None,
        )
        if (
            transition is None
            or firing_input.transition_identity != binding.transition_identity
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                        "transition_validation",
                        "the selected defined transition",
                        "transition identity differs from selected binding",
                    ),
                )
            )
        external = firing_input.external_output_binding
        external_validation = CpnExternalOutputValidator().execute(
            CpnExternalOutputValidationInput(
                definition, transition.identity, external
            )
        )
        if not external_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH,
                        "external_output_validation",
                        "exact declared external-output assignments in order",
                        "external-output binding is incomplete, extra, reordered, or mismatched",
                    ),
                )
            )
        reconstruction = CpnTokenOccurrenceReconstructor().execute(
            CpnTokenOccurrenceReconstructionRequest(
                definition, marking, binding
            )
        )
        if reconstruction.failure is not None:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INPUT_OCCURRENCE_RECONSTRUCTION_FAILED,
                        "input_reconstruction",
                        "one canonical feasible occurrence assignment",
                        "selected value binding cannot be reconstructed",
                    ),
                )
            )
        assert reconstruction.success is not None
        consumed = reconstruction.success.consumed
        read = reconstruction.success.read
        inhibitors = reconstruction.success.inhibitors
        combined = CpnBinding(
            transition.identity, binding.assignments + external.assignments
        )
        produced: list[CpnProducedToken] = []
        evaluator = CpnExpressionEvaluator()
        try:
            for arc in definition.arcs:
                if (
                    arc.transition_identity != transition.identity
                    or arc.output_inscription is None
                ):
                    continue
                for index, template in enumerate(
                    arc.output_inscription.templates
                ):
                    value = evaluator.execute(
                        CpnExpressionEvaluationInput(
                            template.value_expression,
                            combined,
                            definition.control_record_types,
                        )
                    ).value
                    identity = None
                    if template.token_identity_expression is not None:
                        identity_value = evaluator.execute(
                            CpnExpressionEvaluationInput(
                                template.token_identity_expression,
                                combined,
                                definition.control_record_types,
                            )
                        ).value
                        if identity_value.kind is not CpnValueKind.STRING:
                            raise TypeError(
                                "token identity expression must produce string"
                            )
                        assert type(identity_value.value) is str
                        identity = CpnTokenIdentity(identity_value.value)
                    token = CpnToken(template.color_identity, value, identity)
                    produced.append(
                        CpnProducedToken(
                            arc.identity, arc.place_identity, index, token
                        )
                    )
        except (KeyError, TypeError, ValueError) as exc:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.OUTPUT_EVALUATION_FAILED,
                        "output_evaluation",
                        "well-typed total output templates",
                        f"{type(exc).__name__}: {exc}",
                    ),
                )
            )
        consumed_coordinates = {
            (item.place_identity, item.occurrence_ordinal) for item in consumed
        }
        retained_identities = {
            token.token_identity
            for place in marking.places
            for index, token in enumerate(place.tokens)
            if (place.place_identity, index) not in consumed_coordinates
            and token.token_identity is not None
        }
        produced_identities = tuple(
            item.token.token_identity
            for item in produced
            if item.token.token_identity is not None
        )
        if len(set(produced_identities)) != len(produced_identities) or (
            retained_identities & set(produced_identities)
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TOKEN_IDENTITY_COLLISION,
                        "produced_identity_validation",
                        "new unique identities or identities released by consumption",
                        "produced identity is duplicate or collides with a retained token",
                    ),
                )
            )
        audit = CpnFiringAudit(
            consumed, read, inhibitors, tuple(produced), self.identity
        )
        successor = CpnSuccessorMarkingBuilder().execute(
            CpnSuccessorMarkingBuildingRequest(firing_input, audit)
        )
        if (
            not CpnMarkingValidator()
            .execute(CpnMarkingValidationInput(definition, successor))
            .is_valid
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.PRODUCED_TOKEN_INVALID,
                        "successor_validation",
                        "a definition-compatible successor marking",
                        "produced tokens make the successor invalid",
                    ),
                )
            )
        result_identity = CpnFiringResultIdentityDeriver().execute(
            CpnFiringResultIdentityDerivationRequest(
                firing_input, successor=successor, audit=audit
            )
        )
        return CpnFiringResult(
            result_identity,
            firing_input,
            CpnFiringOutcomeKind.SUCCESS,
            successor,
            audit,
        )
