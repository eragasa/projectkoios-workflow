"""Typed child ports, terminal delivery, companion evidence, and cancellation."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256


class WorkflowChildPortDirection(StrEnum):
    """Closed child-port directions."""

    INPUT = "input"
    OUTPUT = "output"


class WorkflowChildPortTrafficKind(StrEnum):
    """Closed child-port traffic roles."""

    INITIAL = "initial"
    EXTERNAL_EVENT = "external_event"
    TERMINAL = "terminal"
    CANCELLATION = "cancellation"
    RECONCILIATION = "reconciliation"


@dataclass(frozen=True, slots=True)
class WorkflowChildPortDefinition:
    """One bounded typed child input or terminal-output port."""

    identity: str
    direction: WorkflowChildPortDirection
    place_identity: str
    color_identity: str
    payload_schema_identity: str | None
    payload_codec_identity: str | None
    scalar_value_kind: str | None
    minimum_token_count: int
    maximum_token_count: int
    correlation_descriptor_identities: tuple[str, ...]
    traffic_kind: WorkflowChildPortTrafficKind
    contract_version: int

    def __post_init__(self) -> None:
        for name in ("identity", "place_identity", "color_identity"):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if not isinstance(self.direction, WorkflowChildPortDirection):
            raise TypeError("direction must be WorkflowChildPortDirection")
        if not isinstance(self.traffic_kind, WorkflowChildPortTrafficKind):
            raise TypeError("traffic_kind must be WorkflowChildPortTrafficKind")
        payload_fields = (
            self.payload_schema_identity,
            self.payload_codec_identity,
        )
        if any(
            item is not None and (type(item) is not str or not item)
            for item in payload_fields
        ):
            raise TypeError(
                "payload schema and codec must be nonempty strings or None"
            )
        has_payload = all(item is not None for item in payload_fields)
        if any(item is not None for item in payload_fields) and not has_payload:
            raise ValueError(
                "payload schema and codec must be declared together"
            )
        if self.scalar_value_kind is not None and (
            type(self.scalar_value_kind) is not str
            or not self.scalar_value_kind
        ):
            raise TypeError(
                "scalar_value_kind must be a nonempty string or None"
            )
        if has_payload == (self.scalar_value_kind is not None):
            raise ValueError(
                "exactly one payload contract or scalar kind is required"
            )
        for name in ("minimum_token_count", "maximum_token_count"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise TypeError(f"{name} must be a nonnegative integer")
        if self.minimum_token_count > self.maximum_token_count:
            raise ValueError("minimum token count must not exceed maximum")
        values = self.correlation_descriptor_identities
        if type(values) is not tuple or any(
            type(item) is not str or not item for item in values
        ):
            raise TypeError(
                "correlation_descriptor_identities must be nonempty strings"
            )
        if values != tuple(sorted(set(values))):
            raise ValueError(
                "correlation_descriptor_identities must be unique and lexical"
            )
        if (
            self.traffic_kind is WorkflowChildPortTrafficKind.TERMINAL
            and self.direction is not WorkflowChildPortDirection.OUTPUT
        ):
            raise ValueError("terminal ports must be output ports")
        if (
            self.traffic_kind is WorkflowChildPortTrafficKind.INITIAL
            and self.direction is not WorkflowChildPortDirection.INPUT
        ):
            raise ValueError("initial ports must be input ports")
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")


class WorkflowCompanionProductionPhase(StrEnum):
    """Closed terminal companion production phases."""

    PRE_TERMINAL_RETAINED = "pre_terminal_retained"
    POST_TERMINAL_PRE_DELIVERY_RETAINED = "post_terminal_pre_delivery_retained"


@dataclass(frozen=True, slots=True)
class WorkflowTerminalCompanionEvidenceRequirement:
    """One ordered bounded content-identified companion requirement."""

    ordinal: int
    evidence_role_identity: str
    owner_identity: str
    payload_schema_identity: str
    codec_identity: str
    media_type_identity: str
    maximum_payload_bytes: int
    minimum_reference_count: int
    maximum_reference_count: int
    production_phase: WorkflowCompanionProductionPhase
    correlation_predicate_descriptor_identity: str
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "evidence_role_identity",
            "owner_identity",
            "payload_schema_identity",
            "codec_identity",
            "media_type_identity",
            "correlation_predicate_descriptor_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if (
            type(self.ordinal) is not int
            or not 0 <= self.ordinal <= 9_223_372_036_854_775_807
        ):
            raise TypeError(
                "ordinal must be a signed-64-bit nonnegative integer"
            )
        if (
            type(self.maximum_payload_bytes) is not int
            or not 1 <= self.maximum_payload_bytes <= 9_223_372_036_854_775_807
        ):
            raise TypeError(
                "maximum_payload_bytes must be a positive signed-64-bit integer"
            )
        for name in ("minimum_reference_count", "maximum_reference_count"):
            value = getattr(self, name)
            if (
                type(value) is not int
                or not 0 <= value <= 9_223_372_036_854_775_807
            ):
                raise TypeError(
                    f"{name} must be a signed-64-bit nonnegative integer"
                )
        if self.maximum_reference_count < 1:
            raise ValueError("maximum_reference_count must be positive")
        if self.minimum_reference_count > self.maximum_reference_count:
            raise ValueError("minimum reference count must not exceed maximum")
        if not isinstance(
            self.production_phase, WorkflowCompanionProductionPhase
        ):
            raise TypeError(
                "production_phase must be WorkflowCompanionProductionPhase"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "codec_identity": self.codec_identity,
            "contract_version": str(self.contract_version),
            "correlation_predicate_descriptor_identity": self.correlation_predicate_descriptor_identity,
            "evidence_role_identity": self.evidence_role_identity,
            "maximum_payload_bytes": str(self.maximum_payload_bytes),
            "maximum_reference_count": str(self.maximum_reference_count),
            "media_type_identity": self.media_type_identity,
            "minimum_reference_count": str(self.minimum_reference_count),
            "ordinal": str(self.ordinal),
            "owner_identity": self.owner_identity,
            "payload_schema_identity": self.payload_schema_identity,
            "production_phase": self.production_phase.value,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.terminal-companion-requirement:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowTerminalDeliveryRequirement:
    """Complete content-identified terminal primary/companion requirement."""

    terminal_classification_identity: str
    primary_terminal_port_identity: str
    primary_payload_schema_identity: str
    primary_payload_codec_identity: str
    companion_requirements: tuple[
        WorkflowTerminalCompanionEvidenceRequirement, ...
    ]
    maximum_total_companion_reference_count: int
    mapper_input_ordering_profile_identity: str
    correlation_validation_descriptor_identity: str
    output_mapper_descriptor_identity: str
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "terminal_classification_identity",
            "primary_terminal_port_identity",
            "primary_payload_schema_identity",
            "primary_payload_codec_identity",
            "mapper_input_ordering_profile_identity",
            "correlation_validation_descriptor_identity",
            "output_mapper_descriptor_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        requirements = self.companion_requirements
        if len(requirements) > 64:
            raise ValueError("at most 64 companion requirements are admitted")
        if type(requirements) is not tuple or any(
            type(item) is not WorkflowTerminalCompanionEvidenceRequirement
            for item in requirements
        ):
            raise TypeError(
                "companion_requirements must be exact companion requirements"
            )
        if tuple(item.ordinal for item in requirements) != tuple(
            range(len(requirements))
        ):
            raise ValueError("companion ordinals must be contiguous from zero")
        identities = tuple(item.identity for item in requirements)
        if len(set(identities)) != len(identities):
            raise ValueError("companion requirement identities must be unique")
        expected_maximum = sum(
            item.maximum_reference_count for item in requirements
        )
        if (
            type(self.maximum_total_companion_reference_count) is not int
            or not 0
            <= self.maximum_total_companion_reference_count
            <= 9_223_372_036_854_775_807
        ):
            raise TypeError(
                "maximum_total_companion_reference_count must be nonnegative"
            )
        if self.maximum_total_companion_reference_count != expected_maximum:
            raise ValueError(
                "maximum total companion count must equal requirement maxima"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "companion_requirement_identities": list(identities),
            "contract_version": str(self.contract_version),
            "correlation_validation_descriptor_identity": self.correlation_validation_descriptor_identity,
            "mapper_input_ordering_profile_identity": self.mapper_input_ordering_profile_identity,
            "maximum_total_companion_reference_count": str(
                self.maximum_total_companion_reference_count
            ),
            "output_mapper_descriptor_identity": self.output_mapper_descriptor_identity,
            "primary_payload_codec_identity": self.primary_payload_codec_identity,
            "primary_payload_schema_identity": self.primary_payload_schema_identity,
            "primary_terminal_port_identity": self.primary_terminal_port_identity,
            "terminal_classification_identity": self.terminal_classification_identity,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.terminal-delivery-requirement:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowChildCancellationCapability:
    """Exact child cancellation topology and runtime capability declaration."""

    identity: str
    in_net_cancellation_supported: bool
    cancellation_port_identities: tuple[str, ...]
    cancellation_terminal_classification_identities: tuple[str, ...]
    propagation_policy_identity: str
    contract_version: int

    def __post_init__(self) -> None:
        for name in ("identity", "propagation_policy_identity"):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if type(self.in_net_cancellation_supported) is not bool:
            raise TypeError("in_net_cancellation_supported must be bool")
        for name in (
            "cancellation_port_identities",
            "cancellation_terminal_classification_identities",
        ):
            values = getattr(self, name)
            if type(values) is not tuple or any(
                type(item) is not str or not item for item in values
            ):
                raise TypeError(f"{name} must be a tuple of nonempty strings")
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{name} must be unique and lexical")
        if not self.in_net_cancellation_supported and (
            self.cancellation_port_identities
            or self.cancellation_terminal_classification_identities
        ):
            raise ValueError(
                "unsupported in-net cancellation must not fabricate ports or terminals"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")


@dataclass(frozen=True, slots=True)
class WorkflowChildInterface:
    """Complete content-identified child port and terminal capability surface."""

    input_ports: tuple[WorkflowChildPortDefinition, ...]
    terminal_output_ports: tuple[WorkflowChildPortDefinition, ...]
    admitted_terminal_classification_identities: tuple[str, ...]
    terminal_delivery_requirements: tuple[
        WorkflowTerminalDeliveryRequirement, ...
    ]
    cancellation_capability: WorkflowChildCancellationCapability
    reconciliation_capability_identity: str
    execution_protocol_requirement_identity: str
    protected_effect_capability_identities: tuple[str, ...]
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.input_ports) is not tuple or any(
            type(item) is not WorkflowChildPortDefinition
            or item.direction is not WorkflowChildPortDirection.INPUT
            for item in self.input_ports
        ):
            raise TypeError("input_ports must contain exact input ports")
        if type(self.terminal_output_ports) is not tuple or any(
            type(item) is not WorkflowChildPortDefinition
            or item.direction is not WorkflowChildPortDirection.OUTPUT
            or item.traffic_kind is not WorkflowChildPortTrafficKind.TERMINAL
            for item in self.terminal_output_ports
        ):
            raise TypeError(
                "terminal_output_ports must contain exact terminal ports"
            )
        port_identities = tuple(
            item.identity
            for item in self.input_ports + self.terminal_output_ports
        )
        if port_identities != tuple(sorted(set(port_identities))):
            raise ValueError("child ports must be unique and identity-ordered")
        classifications = self.admitted_terminal_classification_identities
        if type(classifications) is not tuple or any(
            type(item) is not str or not item for item in classifications
        ):
            raise TypeError("terminal classifications must be nonempty strings")
        if classifications != tuple(sorted(set(classifications))):
            raise ValueError(
                "terminal classifications must be unique and lexical"
            )
        requirements = self.terminal_delivery_requirements
        if type(requirements) is not tuple or any(
            type(item) is not WorkflowTerminalDeliveryRequirement
            for item in requirements
        ):
            raise TypeError("terminal delivery requirements have invalid types")
        if (
            tuple(
                item.terminal_classification_identity for item in requirements
            )
            != classifications
        ):
            raise ValueError(
                "terminal requirements must exactly follow classifications"
            )
        terminal_ports = {
            item.identity: item for item in self.terminal_output_ports
        }
        for requirement in requirements:
            port = terminal_ports.get(
                requirement.primary_terminal_port_identity
            )
            if port is None:
                raise ValueError(
                    "terminal requirement references an unknown port"
                )
            if port.minimum_token_count != 1 or port.maximum_token_count != 1:
                raise ValueError(
                    "primary terminal port must require exactly one payload"
                )
            if (
                port.payload_schema_identity
                != requirement.primary_payload_schema_identity
                or port.payload_codec_identity
                != requirement.primary_payload_codec_identity
            ):
                raise ValueError(
                    "terminal requirement differs from its primary port"
                )
        if (
            type(self.cancellation_capability)
            is not WorkflowChildCancellationCapability
        ):
            raise TypeError("cancellation_capability has the wrong type")
        input_ports = {item.identity: item for item in self.input_ports}
        for (
            port_identity
        ) in self.cancellation_capability.cancellation_port_identities:
            port = input_ports.get(port_identity)
            if (
                port is None
                or port.traffic_kind
                is not WorkflowChildPortTrafficKind.CANCELLATION
            ):
                raise ValueError(
                    "cancellation capability references an invalid input port"
                )
        cancellation_classes = set(
            self.cancellation_capability.cancellation_terminal_classification_identities
        )
        if not cancellation_classes <= set(classifications):
            raise ValueError(
                "cancellation terminal classifications must be admitted terminals"
            )
        for name in (
            "reconciliation_capability_identity",
            "execution_protocol_requirement_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be nonempty")
        effects = self.protected_effect_capability_identities
        if type(effects) is not tuple or any(
            type(item) is not str or not item for item in effects
        ):
            raise TypeError(
                "protected effect capabilities must be nonempty strings"
            )
        if effects != tuple(sorted(set(effects))):
            raise ValueError(
                "protected effect capabilities must be unique and lexical"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be positive")
        state = {
            "cancellation_capability": {
                "cancellation_port_identities": list(
                    self.cancellation_capability.cancellation_port_identities
                ),
                "cancellation_terminal_classification_identities": list(
                    self.cancellation_capability.cancellation_terminal_classification_identities
                ),
                "contract_version": str(
                    self.cancellation_capability.contract_version
                ),
                "identity": self.cancellation_capability.identity,
                "in_net_cancellation_supported": self.cancellation_capability.in_net_cancellation_supported,
                "propagation_policy_identity": self.cancellation_capability.propagation_policy_identity,
            },
            "classifications": list(classifications),
            "contract_version": str(self.contract_version),
            "input_ports": [
                {
                    "color_identity": item.color_identity,
                    "contract_version": str(item.contract_version),
                    "correlation_descriptor_identities": list(
                        item.correlation_descriptor_identities
                    ),
                    "direction": item.direction.value,
                    "identity": item.identity,
                    "maximum_token_count": str(item.maximum_token_count),
                    "minimum_token_count": str(item.minimum_token_count),
                    "payload_codec_identity": item.payload_codec_identity,
                    "payload_schema_identity": item.payload_schema_identity,
                    "place_identity": item.place_identity,
                    "scalar_value_kind": item.scalar_value_kind,
                    "traffic_kind": item.traffic_kind.value,
                }
                for item in self.input_ports
            ],
            "execution_protocol_requirement_identity": self.execution_protocol_requirement_identity,
            "protected_effect_capability_identities": list(effects),
            "reconciliation_capability_identity": self.reconciliation_capability_identity,
            "terminal_delivery_requirement_identities": [
                item.identity for item in requirements
            ],
            "terminal_output_ports": [
                {
                    "color_identity": item.color_identity,
                    "contract_version": str(item.contract_version),
                    "correlation_descriptor_identities": list(
                        item.correlation_descriptor_identities
                    ),
                    "direction": item.direction.value,
                    "identity": item.identity,
                    "maximum_token_count": str(item.maximum_token_count),
                    "minimum_token_count": str(item.minimum_token_count),
                    "payload_codec_identity": item.payload_codec_identity,
                    "payload_schema_identity": item.payload_schema_identity,
                    "place_identity": item.place_identity,
                    "scalar_value_kind": item.scalar_value_kind,
                    "traffic_kind": item.traffic_kind.value,
                }
                for item in self.terminal_output_ports
            ],
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.child-interface:0.1:"
            + sha256(encoded).hexdigest(),
        )
