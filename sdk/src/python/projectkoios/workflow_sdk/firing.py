"""Runtime-enforced pure firing records and nominal integration ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from . import WORKFLOW_SDK_VERSION
from ._validation import (
    MAX_CONTRACTS,
    MAX_PAYLOAD_COUNT,
    MAX_REASON_COUNT,
    MAX_TOTAL_PAYLOAD_BYTES,
    semantic_sha256,
    unique,
    validate_nonnegative_int,
    validate_sdk_version,
    validate_sha256,
    validate_token,
)
from .identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
    WorkflowTransitionBindingIdentity,
    WorkflowTransitionIdentity,
)
from .payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
    payload_contract_state,
    payload_state,
)


@dataclass(frozen=True, slots=True)
class WorkflowFiringBounds:
    """Bound one pure firer's requests, results, evidence, and reasons."""

    maximum_input_count: int
    maximum_output_count: int
    maximum_evidence_count: int
    maximum_input_bytes: int
    maximum_output_bytes: int
    maximum_total_bytes: int
    maximum_reason_count: int

    def __post_init__(self) -> None:
        for name, maximum in (
            ("maximum_input_count", MAX_PAYLOAD_COUNT),
            ("maximum_output_count", MAX_PAYLOAD_COUNT),
            ("maximum_evidence_count", MAX_PAYLOAD_COUNT),
            ("maximum_input_bytes", MAX_TOTAL_PAYLOAD_BYTES),
            ("maximum_output_bytes", MAX_TOTAL_PAYLOAD_BYTES),
            ("maximum_total_bytes", MAX_TOTAL_PAYLOAD_BYTES),
            ("maximum_reason_count", MAX_REASON_COUNT),
        ):
            value = getattr(self, name)
            validate_nonnegative_int(value, name)
            if value > maximum:
                raise ValueError(f"{name} exceeds SDK hard limit {maximum}")
        if self.maximum_total_bytes < max(
            self.maximum_input_bytes,
            self.maximum_output_bytes,
        ):
            raise ValueError(
                "maximum_total_bytes must admit input and output byte bounds"
            )


@dataclass(frozen=True, slots=True)
class WorkflowFirerDescriptor:
    """Describe one exact pure owner integration operation."""

    identity: WorkflowFirerIdentity
    implementation_identity: WorkflowFirerImplementationIdentity
    input_contracts: tuple[WorkflowPayloadContract, ...]
    output_contracts: tuple[WorkflowPayloadContract, ...]
    evidence_contracts: tuple[WorkflowPayloadContract, ...]
    bounds: WorkflowFiringBounds
    sdk_contract_version: str = WORKFLOW_SDK_VERSION

    def __post_init__(self) -> None:
        if type(self.identity) is not WorkflowFirerIdentity:
            raise TypeError("identity must be WorkflowFirerIdentity")
        if type(self.implementation_identity) is not (
            WorkflowFirerImplementationIdentity
        ):
            raise TypeError(
                "implementation_identity must be WorkflowFirerImplementationIdentity"
            )
        for name in (
            "input_contracts",
            "output_contracts",
            "evidence_contracts",
        ):
            contracts = getattr(self, name)
            _require_exact_tuple(
                contracts,
                WorkflowPayloadContract,
                name,
                MAX_CONTRACTS,
            )
            roles = tuple(contract.role for contract in contracts)
            unique(roles, f"{name} roles")
        if type(self.bounds) is not WorkflowFiringBounds:
            raise TypeError("bounds must be WorkflowFiringBounds")
        validate_sdk_version(self.sdk_contract_version, WORKFLOW_SDK_VERSION)
        if len(self.input_contracts) > self.bounds.maximum_input_count:
            raise ValueError("input contracts exceed descriptor bounds")
        if len(self.output_contracts) > self.bounds.maximum_output_count:
            raise ValueError("output contracts exceed descriptor bounds")
        if len(self.evidence_contracts) > self.bounds.maximum_evidence_count:
            raise ValueError("evidence contracts exceed descriptor bounds")
        input_bytes = sum(c.maximum_byte_length for c in self.input_contracts)
        output_bytes = sum(c.maximum_byte_length for c in self.output_contracts)
        evidence_bytes = sum(c.maximum_byte_length for c in self.evidence_contracts)
        if input_bytes > self.bounds.maximum_input_bytes:
            raise ValueError("input contract bytes exceed descriptor bounds")
        if output_bytes > self.bounds.maximum_output_bytes:
            raise ValueError("output contract bytes exceed descriptor bounds")
        if max(input_bytes, output_bytes + evidence_bytes) > (
            self.bounds.maximum_total_bytes
        ):
            raise ValueError("contract bytes exceed descriptor total bound")


@dataclass(frozen=True, slots=True)
class WorkflowOccurrenceContext:
    """Correlate one pure integration attempt to one selected CPN binding."""

    definition_identity: WorkflowDefinitionIdentity
    net_instance_identity: WorkflowNetInstanceIdentity
    transition_identity: WorkflowTransitionIdentity
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    selected_binding_sha256: str
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    attempt_ordinal: int

    def __post_init__(self) -> None:
        for name, expected in (
            ("definition_identity", WorkflowDefinitionIdentity),
            ("net_instance_identity", WorkflowNetInstanceIdentity),
            ("transition_identity", WorkflowTransitionIdentity),
            ("predecessor_marking_identity", WorkflowMarkingIdentity),
            ("occurrence_identity", WorkflowOccurrenceIdentity),
            ("attempt_identity", WorkflowAttemptIdentity),
        ):
            if type(getattr(self, name)) is not expected:
                raise TypeError(f"{name} must be {expected.__name__}")
        validate_nonnegative_int(self.predecessor_revision, "predecessor_revision")
        validate_sha256(self.selected_binding_sha256, "selected_binding_sha256")
        validate_nonnegative_int(self.attempt_ordinal, "attempt_ordinal")


@dataclass(frozen=True, slots=True)
class WorkflowTransitionFirerBinding:
    """Bind one immutable Workflow transition to one advertised firer."""

    identity: WorkflowTransitionBindingIdentity = field(init=False)
    definition_identity: WorkflowDefinitionIdentity
    transition_identity: WorkflowTransitionIdentity
    firer_identity: WorkflowFirerIdentity
    input_roles: tuple[str, ...]
    output_roles: tuple[str, ...]
    binding_version: str

    def __post_init__(self) -> None:
        if type(self.definition_identity) is not WorkflowDefinitionIdentity:
            raise TypeError("definition_identity must be WorkflowDefinitionIdentity")
        if type(self.transition_identity) is not WorkflowTransitionIdentity:
            raise TypeError("transition_identity must be WorkflowTransitionIdentity")
        if type(self.firer_identity) is not WorkflowFirerIdentity:
            raise TypeError("firer_identity must be WorkflowFirerIdentity")
        for name in ("input_roles", "output_roles"):
            roles = getattr(self, name)
            if type(roles) is not tuple:
                raise TypeError(f"{name} must be a tuple")
            if len(roles) > MAX_PAYLOAD_COUNT:
                raise ValueError(f"{name} exceeds {MAX_PAYLOAD_COUNT} entries")
            for role in roles:
                validate_token(role, f"{name} role")
            unique(roles, name)
        validate_token(self.binding_version, "binding_version")
        object.__setattr__(
            self,
            "identity",
            WorkflowTransitionBindingIdentity(
                semantic_sha256(
                    "workflow-sdk-transition-firer-binding:1",
                    binding_state(self),
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class WorkflowFiringRequest:
    """Carry one exact bounded pure invocation to a registered firer."""

    identity: WorkflowFiringRequestIdentity = field(init=False)
    context: WorkflowOccurrenceContext
    binding_identity: WorkflowTransitionBindingIdentity
    firer_identity: WorkflowFirerIdentity
    inputs: tuple[WorkflowInlinePayload, ...]
    sdk_contract_version: str = WORKFLOW_SDK_VERSION

    def __post_init__(self) -> None:
        if type(self.context) is not WorkflowOccurrenceContext:
            raise TypeError("context must be WorkflowOccurrenceContext")
        if type(self.binding_identity) is not WorkflowTransitionBindingIdentity:
            raise TypeError(
                "binding_identity must be WorkflowTransitionBindingIdentity"
            )
        if type(self.firer_identity) is not WorkflowFirerIdentity:
            raise TypeError("firer_identity must be WorkflowFirerIdentity")
        _require_exact_tuple(
            self.inputs,
            WorkflowInlinePayload,
            "inputs",
            MAX_PAYLOAD_COUNT,
        )
        unique(tuple(value.role for value in self.inputs), "input roles")
        if sum(value.byte_length for value in self.inputs) > MAX_TOTAL_PAYLOAD_BYTES:
            raise ValueError("input bytes exceed SDK hard limit")
        validate_sdk_version(self.sdk_contract_version, WORKFLOW_SDK_VERSION)
        object.__setattr__(
            self,
            "identity",
            WorkflowFiringRequestIdentity(
                semantic_sha256(
                    "workflow-sdk-firing-request:1",
                    request_state(self),
                )
            ),
        )


class WorkflowFiringResult(ABC):
    """Nominal base for the closed pure-firing result variants."""

    __slots__ = ()

    identity: WorkflowFiringResultIdentity
    request_identity: WorkflowFiringRequestIdentity
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    firer_identity: WorkflowFirerIdentity
    evidence: tuple[WorkflowInlinePayload, ...]
    sdk_contract_version: str

    @classmethod
    @abstractmethod
    def _outcome(cls) -> str:
        """Return the private closed-variant discriminator."""


@dataclass(frozen=True, slots=True)
class WorkflowFiringSucceeded(WorkflowFiringResult):
    """Return correlated candidate outputs and evidence without firing the CPN."""

    identity: WorkflowFiringResultIdentity = field(init=False)
    request_identity: WorkflowFiringRequestIdentity
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    firer_identity: WorkflowFirerIdentity
    outputs: tuple[WorkflowInlinePayload, ...]
    evidence: tuple[WorkflowInlinePayload, ...]
    sdk_contract_version: str = WORKFLOW_SDK_VERSION

    def __post_init__(self) -> None:
        _validate_result_common(self)
        _require_payload_tuple(self.outputs, "outputs")
        _require_payload_tuple(self.evidence, "evidence")
        object.__setattr__(self, "identity", _result_identity("succeeded", self))

    @classmethod
    def _outcome(cls) -> str:
        return "succeeded"


@dataclass(frozen=True, slots=True)
class WorkflowFiringRejected(WorkflowFiringResult):
    """Reject one pure request without producing candidate outputs."""

    identity: WorkflowFiringResultIdentity = field(init=False)
    request_identity: WorkflowFiringRequestIdentity
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    firer_identity: WorkflowFirerIdentity
    reason_codes: tuple[str, ...]
    evidence: tuple[WorkflowInlinePayload, ...]
    sdk_contract_version: str = WORKFLOW_SDK_VERSION

    def __post_init__(self) -> None:
        _validate_result_common(self)
        _validate_codes(self.reason_codes, "reason_codes")
        _require_payload_tuple(self.evidence, "evidence")
        object.__setattr__(self, "identity", _result_identity("rejected", self))

    @classmethod
    def _outcome(cls) -> str:
        return "rejected"


@dataclass(frozen=True, slots=True)
class WorkflowFiringFailed(WorkflowFiringResult):
    """Report one known effect-free invocation failure."""

    identity: WorkflowFiringResultIdentity = field(init=False)
    request_identity: WorkflowFiringRequestIdentity
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    firer_identity: WorkflowFirerIdentity
    failure_codes: tuple[str, ...]
    evidence: tuple[WorkflowInlinePayload, ...]
    sdk_contract_version: str = WORKFLOW_SDK_VERSION

    def __post_init__(self) -> None:
        _validate_result_common(self)
        _validate_codes(self.failure_codes, "failure_codes")
        _require_payload_tuple(self.evidence, "evidence")
        object.__setattr__(self, "identity", _result_identity("failed", self))

    @classmethod
    def _outcome(cls) -> str:
        return "failed"


_ALLOWED_RESULT_TYPES = (
    WorkflowFiringSucceeded,
    WorkflowFiringRejected,
    WorkflowFiringFailed,
)


class Firer(ABC):
    """Runtime-enforced entry point for one registered pure integration."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "fire" in cls.__dict__:
            raise TypeError("Firer.fire is a non-overridable template method")

    @property
    @abstractmethod
    def descriptor(self) -> WorkflowFirerDescriptor:
        """Return the exact immutable descriptor for this firer."""

    def fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
        """Validate, invoke, and correlate one pure firing request."""
        if type(request) is not WorkflowFiringRequest:
            raise TypeError("request must be WorkflowFiringRequest")
        descriptor = self.descriptor
        if type(descriptor) is not WorkflowFirerDescriptor:
            raise TypeError("descriptor must be WorkflowFirerDescriptor")
        if request.firer_identity != descriptor.identity:
            raise ValueError("request firer identity differs from descriptor")
        _validate_payload_sequence(
            request.inputs,
            descriptor.input_contracts,
            exact=True,
            label="inputs",
        )
        if len(request.inputs) > descriptor.bounds.maximum_input_count:
            raise ValueError("request input count exceeds descriptor bounds")
        input_bytes = sum(value.byte_length for value in request.inputs)
        if input_bytes > descriptor.bounds.maximum_input_bytes:
            raise ValueError("request input bytes exceed descriptor bounds")
        if input_bytes > descriptor.bounds.maximum_total_bytes:
            raise ValueError("request bytes exceed descriptor total bound")

        result = self._fire(request=request)
        if type(result) not in _ALLOWED_RESULT_TYPES:
            raise TypeError("firer returned an unsupported result type")
        _validate_result_correlation(descriptor, request, result)
        return result

    @abstractmethod
    def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
        """Implement one consumer-owned pure integration operation."""


def descriptor_state(value: WorkflowFirerDescriptor) -> list[object]:
    """Return private canonical descriptor semantic state."""
    return [
        value.identity.value,
        value.implementation_identity.value,
        [payload_contract_state(item) for item in value.input_contracts],
        [payload_contract_state(item) for item in value.output_contracts],
        [payload_contract_state(item) for item in value.evidence_contracts],
        bounds_state(value.bounds),
        value.sdk_contract_version,
    ]


def bounds_state(value: WorkflowFiringBounds) -> list[int]:
    """Return private canonical bounds state."""
    return [
        value.maximum_input_count,
        value.maximum_output_count,
        value.maximum_evidence_count,
        value.maximum_input_bytes,
        value.maximum_output_bytes,
        value.maximum_total_bytes,
        value.maximum_reason_count,
    ]


def context_state(value: WorkflowOccurrenceContext) -> list[object]:
    """Return private canonical occurrence-context state."""
    return [
        value.definition_identity.value,
        value.net_instance_identity.value,
        value.transition_identity.value,
        value.predecessor_marking_identity.value,
        value.predecessor_revision,
        value.selected_binding_sha256,
        value.occurrence_identity.value,
        value.attempt_identity.value,
        value.attempt_ordinal,
    ]


def binding_state(value: WorkflowTransitionFirerBinding) -> list[object]:
    """Return binding state excluding its derived identity."""
    return [
        value.definition_identity.value,
        value.transition_identity.value,
        value.firer_identity.value,
        list(value.input_roles),
        list(value.output_roles),
        value.binding_version,
    ]


def request_state(value: WorkflowFiringRequest) -> list[object]:
    """Return request state excluding its derived identity and inline duplication."""
    return [
        context_state(value.context),
        value.binding_identity.value,
        value.firer_identity.value,
        [payload_state(item) for item in value.inputs],
        value.sdk_contract_version,
    ]


def result_state(
    outcome: str,
    value: WorkflowFiringSucceeded | WorkflowFiringRejected | WorkflowFiringFailed,
) -> list[object]:
    """Return result state excluding its derived identity."""
    common: list[object] = [
        outcome,
        value.request_identity.value,
        value.occurrence_identity.value,
        value.attempt_identity.value,
        value.firer_identity.value,
    ]
    if type(value) is WorkflowFiringSucceeded:
        common.extend(
            [
                [payload_state(item) for item in value.outputs],
                [payload_state(item) for item in value.evidence],
            ]
        )
    elif type(value) is WorkflowFiringRejected:
        common.extend(
            [
                list(value.reason_codes),
                [payload_state(item) for item in value.evidence],
            ]
        )
    else:
        assert type(value) is WorkflowFiringFailed
        common.extend(
            [
                list(value.failure_codes),
                [payload_state(item) for item in value.evidence],
            ]
        )
    common.append(value.sdk_contract_version)
    return common


def _result_identity(
    outcome: str,
    value: WorkflowFiringSucceeded | WorkflowFiringRejected | WorkflowFiringFailed,
) -> WorkflowFiringResultIdentity:
    return WorkflowFiringResultIdentity(
        semantic_sha256(
            f"workflow-sdk-firing-result-{outcome}:1",
            result_state(outcome, value),
        )
    )


def _validate_result_common(
    value: WorkflowFiringSucceeded | WorkflowFiringRejected | WorkflowFiringFailed,
) -> None:
    for name, expected in (
        ("request_identity", WorkflowFiringRequestIdentity),
        ("occurrence_identity", WorkflowOccurrenceIdentity),
        ("attempt_identity", WorkflowAttemptIdentity),
        ("firer_identity", WorkflowFirerIdentity),
    ):
        if type(getattr(value, name)) is not expected:
            raise TypeError(f"{name} must be {expected.__name__}")
    validate_sdk_version(value.sdk_contract_version, WORKFLOW_SDK_VERSION)


def _validate_codes(values: tuple[str, ...], label: str) -> None:
    if type(values) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if not values or len(values) > MAX_REASON_COUNT:
        raise ValueError(f"{label} must contain 1..{MAX_REASON_COUNT} values")
    for value in values:
        validate_token(value, label)
    if values != tuple(sorted(set(values))):
        raise ValueError(f"{label} must be unique and canonically sorted")


def _require_payload_tuple(values: object, label: str) -> None:
    _require_exact_tuple(values, WorkflowInlinePayload, label, MAX_PAYLOAD_COUNT)
    assert type(values) is tuple
    unique(tuple(value.role for value in values), f"{label} roles")
    if sum(value.byte_length for value in values) > MAX_TOTAL_PAYLOAD_BYTES:
        raise ValueError(f"{label} bytes exceed SDK hard limit")


def _require_exact_tuple(
    values: object,
    item_type: type[object],
    label: str,
    maximum: int,
) -> None:
    if type(values) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if len(values) > maximum:
        raise ValueError(f"{label} exceeds {maximum} entries")
    if any(type(value) is not item_type for value in values):
        raise TypeError(f"{label} contains an invalid item type")


def _validate_payload_sequence(
    payloads: tuple[WorkflowInlinePayload, ...],
    contracts: tuple[WorkflowPayloadContract, ...],
    *,
    exact: bool,
    label: str,
) -> None:
    contract_by_role = {value.role: value for value in contracts}
    contract_positions = {value.role: index for index, value in enumerate(contracts)}
    positions: list[int] = []
    for payload in payloads:
        contract = contract_by_role.get(payload.role)
        if contract is None:
            raise ValueError(f"{label} contains unregistered role {payload.role}")
        if (
            payload.owner_identity != contract.owner_identity
            or payload.payload_type_identity != contract.payload_type_identity
            or payload.schema_identity != contract.schema_identity
            or payload.codec_identity != contract.codec_identity
            or payload.representation_identity != contract.representation_identity
            or payload.media_type != contract.media_type
        ):
            raise ValueError(f"{label} payload metadata differs from contract")
        if payload.byte_length > contract.maximum_byte_length:
            raise ValueError(f"{label} payload exceeds role byte bound")
        positions.append(contract_positions[payload.role])
    if positions != sorted(positions):
        raise ValueError(f"{label} roles differ from descriptor order")
    if exact and len(payloads) != len(contracts):
        raise ValueError(f"{label} must satisfy every declared contract")


def _validate_result_correlation(
    descriptor: WorkflowFirerDescriptor,
    request: WorkflowFiringRequest,
    result: WorkflowFiringResult,
) -> None:
    assert type(result) in _ALLOWED_RESULT_TYPES
    if (
        result.request_identity != request.identity
        or result.occurrence_identity != request.context.occurrence_identity
        or result.attempt_identity != request.context.attempt_identity
        or result.firer_identity != descriptor.identity
        or result.sdk_contract_version != WORKFLOW_SDK_VERSION
    ):
        raise ValueError("firing result correlation differs from request")
    evidence = result.evidence
    _validate_payload_sequence(
        evidence,
        descriptor.evidence_contracts,
        exact=False,
        label="evidence",
    )
    if len(evidence) > descriptor.bounds.maximum_evidence_count:
        raise ValueError("result evidence count exceeds descriptor bounds")
    if type(result) is WorkflowFiringSucceeded:
        _validate_payload_sequence(
            result.outputs,
            descriptor.output_contracts,
            exact=True,
            label="outputs",
        )
        if len(result.outputs) > descriptor.bounds.maximum_output_count:
            raise ValueError("result output count exceeds descriptor bounds")
        output_bytes = sum(item.byte_length for item in result.outputs)
        if output_bytes > descriptor.bounds.maximum_output_bytes:
            raise ValueError("result output bytes exceed descriptor bounds")
    else:
        output_bytes = 0
        if type(result) is WorkflowFiringRejected:
            codes = result.reason_codes
        else:
            assert type(result) is WorkflowFiringFailed
            codes = result.failure_codes
        if len(codes) > descriptor.bounds.maximum_reason_count:
            raise ValueError("result codes exceed descriptor bounds")
    evidence_bytes = sum(item.byte_length for item in evidence)
    if output_bytes + evidence_bytes > descriptor.bounds.maximum_total_bytes:
        raise ValueError("result bytes exceed descriptor total bound")


__all__ = [
    "Firer",
    "WorkflowFirerDescriptor",
    "WorkflowFiringBounds",
    "WorkflowFiringFailed",
    "WorkflowFiringRejected",
    "WorkflowFiringRequest",
    "WorkflowFiringResult",
    "WorkflowFiringSucceeded",
    "WorkflowOccurrenceContext",
    "WorkflowTransitionFirerBinding",
]
