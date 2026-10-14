"""Immutable generic colored-Petri-net graph definitions.

Definitions compose nominal colors, places, transitions, arcs, closed guards,
and inscriptions without embedding a marking, Workflow payload policy, effects,
persistence, or a wire version. Intrinsic collection identity and total-priority
invariants are enforced here; graph references, admitted values, variable
completeness, and definition/marking compatibility belong to the structural
validator.
"""

from dataclasses import dataclass
from enum import StrEnum

from .expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnInputInscription,
    CpnOutputInscription,
)
from .values import (
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
    CpnColorIdentity,
    CpnValueKind,
)


@dataclass(frozen=True, slots=True)
class CpnDefinitionIdentity:
    """Nominal identity of one exact generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity. Canonical encoding and wire
        derivation remain deferred.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the exact built-in nonempty string boundary."""
        if type(self.value) is not str:
            raise TypeError("definition identity value must be a string")
        if not self.value:
            raise ValueError("definition identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnPlaceIdentity:
    """Nominal identity of one place in a generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the exact built-in nonempty string boundary."""
        if type(self.value) is not str:
            raise TypeError("place identity value must be a string")
        if not self.value:
            raise ValueError("place identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnTransitionIdentity:
    """Nominal identity of one transition in a generic net definition.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the exact built-in nonempty string boundary."""
        if type(self.value) is not str:
            raise TypeError("transition identity value must be a string")
        if not self.value:
            raise ValueError("transition identity value must not be empty")


class CpnSelectionPolicy(StrEnum):
    """Definition-owned permission for binding selection.

    ``DETERMINISTIC_ONLY`` permits only canonical default selection.
    ``DIRECTED_ALLOWED`` additionally permits an explicit identity-bound directive.
    """

    DETERMINISTIC_ONLY = "deterministic_only"
    DIRECTED_ALLOWED = "directed_allowed"


@dataclass(frozen=True, slots=True)
class CpnArcIdentity:
    """Nominal identity of one generic directed arc.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity; canonical wire encoding remains
        deferred.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the minimal owner-local lexical boundary."""
        if type(self.value) is not str:
            raise TypeError("arc identity value must be a string")
        if not self.value:
            raise ValueError("arc identity value must not be empty")


@dataclass(frozen=True, slots=True)
class CpnColorDefinition:
    """One generic token color and its admitted tagged value kinds.

    Parameters
    ----------
    identity
        Nominal color identity.
    allowed_value_kinds
        Nonempty unique admitted generic kinds, stored in canonical enum-value
        order. Workflow payload-type identities do not belong to this record.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or the kind collection is mutable.
    ValueError
        The admitted kind set is empty or contains duplicates.

    Notes
    -----
    A legacy no-payload color is represented explicitly by the singleton
    ``NONE`` kind rather than an empty admitted set.
    """

    identity: CpnColorIdentity
    allowed_value_kinds: tuple[CpnValueKind, ...]
    allowed_control_record_type_identities: tuple[
        CpnControlRecordTypeIdentity, ...
    ] = ()

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned admitted-kind set."""
        if type(self.identity) is not CpnColorIdentity:
            raise TypeError("identity must be CpnColorIdentity")
        if type(self.allowed_value_kinds) is not tuple or any(
            not isinstance(kind, CpnValueKind)
            for kind in self.allowed_value_kinds
        ):
            raise TypeError(
                "allowed_value_kinds must be a tuple of CpnValueKind"
            )
        if not self.allowed_value_kinds:
            raise ValueError("allowed_value_kinds must not be empty")
        if len(set(self.allowed_value_kinds)) != len(self.allowed_value_kinds):
            raise ValueError("allowed_value_kinds must be unique")
        ordered_kinds = [
            (item.value, item) for item in self.allowed_value_kinds
        ]
        ordered_kinds.sort()
        object.__setattr__(
            self,
            "allowed_value_kinds",
            tuple(item[1] for item in ordered_kinds),
        )
        record_types = self.allowed_control_record_type_identities
        if type(record_types) is not tuple or any(
            type(item) is not CpnControlRecordTypeIdentity
            for item in record_types
        ):
            raise TypeError(
                "allowed_control_record_type_identities must be a tuple of "
                "CpnControlRecordTypeIdentity"
            )
        if len(set(record_types)) != len(record_types):
            raise ValueError("admitted control-record types must be unique")
        ordered_record_types = [(item.value, item) for item in record_types]
        ordered_record_types.sort()
        object.__setattr__(
            self,
            "allowed_control_record_type_identities",
            tuple(item[1] for item in ordered_record_types),
        )
        if (CpnValueKind.CONTROL_RECORD in self.allowed_value_kinds) != bool(
            record_types
        ):
            raise ValueError(
                "CONTROL_RECORD and exact admitted record types must be declared together"
            )


@dataclass(frozen=True, slots=True)
class CpnPlaceDefinition:
    """One generic place and its admitted color set.

    Parameters
    ----------
    identity
        Nominal place identity.
    allowed_color_identities
        Nonempty unique admitted colors in canonical identity order.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or the color collection is mutable.
    ValueError
        The admitted color set is empty or contains duplicates.
    """

    identity: CpnPlaceIdentity
    allowed_color_identities: tuple[CpnColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned admitted-color set."""
        if type(self.identity) is not CpnPlaceIdentity:
            raise TypeError("identity must be CpnPlaceIdentity")
        if type(self.allowed_color_identities) is not tuple or any(
            type(color) is not CpnColorIdentity
            for color in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of CpnColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        ordered_colors = [
            (item.value, item) for item in self.allowed_color_identities
        ]
        ordered_colors.sort()
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(item[1] for item in ordered_colors),
        )


@dataclass(frozen=True, slots=True)
class CpnTransitionDefinition:
    """One generic transition with declared variable order and a pure guard.

    Parameters
    ----------
    identity
        Nominal transition identity.
    input_variable_identities
        Unique variables in exact definition-declared input-binding order.
    external_output_variable_identities
        Unique variables supplied only through the future explicit external-output
        binding. The two collections are disjoint.
    guard
        Closed pure guard; use ``TRUE`` for an unconditional transition.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or variable collection is mutable.
    ValueError
        A binding variable identity occurs more than once.
    """

    identity: CpnTransitionIdentity
    input_variable_identities: tuple[CpnBindingVariableIdentity, ...]
    external_output_variable_identities: tuple[CpnBindingVariableIdentity, ...]
    guard: CpnGuardExpression

    def __post_init__(self) -> None:
        """Validate intrinsic transition fields while preserving variable order."""
        if type(self.identity) is not CpnTransitionIdentity:
            raise TypeError("identity must be CpnTransitionIdentity")
        for field_name in (
            "input_variable_identities",
            "external_output_variable_identities",
        ):
            variables = getattr(self, field_name)
            if type(variables) is not tuple or any(
                type(item) is not CpnBindingVariableIdentity
                for item in variables
            ):
                raise TypeError(
                    f"{field_name} must be a tuple of "
                    "CpnBindingVariableIdentity"
                )
            if len(set(variables)) != len(variables):
                raise ValueError(f"{field_name} must be unique")
        if set(self.input_variable_identities) & set(
            self.external_output_variable_identities
        ):
            raise ValueError(
                "input and external-output variables must be disjoint"
            )
        if type(self.guard) is not CpnGuardExpression:
            raise TypeError("guard must be CpnGuardExpression")


@dataclass(frozen=True, slots=True)
class CpnArcDefinition:
    """One identified directed arc with exactly one inscription variant.

    Parameters
    ----------
    identity
        Nominal arc identity.
    place_identity
        Referenced nominal place identity.
    transition_identity
        Referenced nominal transition identity.
    input_inscription
        Input demand for a place-to-transition arc, mutually exclusive with output.
    output_inscription
        Output templates for a transition-to-place arc, mutually exclusive with input.

    Raises
    ------
    TypeError
        A field has the wrong nominal type.
    ValueError
        Both inscription variants are present or both are absent.

    Notes
    -----
    Direction is derived from the closed inscription variant and is not duplicated
    as independent state.
    """

    identity: CpnArcIdentity
    place_identity: CpnPlaceIdentity
    transition_identity: CpnTransitionIdentity
    input_inscription: CpnInputInscription | None = None
    output_inscription: CpnOutputInscription | None = None

    def __post_init__(self) -> None:
        """Validate nominal references and exact inscription discrimination."""
        if type(self.identity) is not CpnArcIdentity:
            raise TypeError("identity must be CpnArcIdentity")
        if type(self.place_identity) is not CpnPlaceIdentity:
            raise TypeError("place_identity must be CpnPlaceIdentity")
        if type(self.transition_identity) is not CpnTransitionIdentity:
            raise TypeError("transition_identity must be CpnTransitionIdentity")
        if self.input_inscription is not None and (
            type(self.input_inscription) is not CpnInputInscription
        ):
            raise TypeError(
                "input_inscription must be CpnInputInscription or None"
            )
        if self.output_inscription is not None and (
            type(self.output_inscription) is not CpnOutputInscription
        ):
            raise TypeError(
                "output_inscription must be CpnOutputInscription or None"
            )
        if (self.input_inscription is None) == (
            self.output_inscription is None
        ):
            raise ValueError(
                "exactly one arc inscription variant must be present"
            )


@dataclass(frozen=True, slots=True)
class CpnDefinition:
    """One immutable identified generic colored-Petri-net definition.

    Parameters
    ----------
    identity
        Nominal identity of this exact definition.
    colors, places, transitions, arcs
        Unique definition components stored in canonical nominal-identity order.
    transition_priority
        Exact permutation of every transition identity from highest to lowest
        definition-owned selection priority.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or a collection is mutable.
    ValueError
        Component identities are duplicated or priority is not an exact transition
        identity permutation.

    Notes
    -----
    The definition contains no schema version, initial marking, descriptions,
    Workflow payload identifiers, or external behavior. Cross-reference integrity
    and semantic compatibility belong to ``CpnDefinitionValidator``.
    """

    identity: CpnDefinitionIdentity
    colors: tuple[CpnColorDefinition, ...]
    places: tuple[CpnPlaceDefinition, ...]
    transitions: tuple[CpnTransitionDefinition, ...]
    arcs: tuple[CpnArcDefinition, ...]
    transition_priority: tuple[CpnTransitionIdentity, ...]
    selection_policy: CpnSelectionPolicy = CpnSelectionPolicy.DETERMINISTIC_ONLY
    control_record_types: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        """Validate intrinsic collections, canonicalize them, and close priority."""
        if type(self.identity) is not CpnDefinitionIdentity:
            raise TypeError("identity must be CpnDefinitionIdentity")
        collections = (
            ("colors", CpnColorDefinition),
            ("places", CpnPlaceDefinition),
            ("transitions", CpnTransitionDefinition),
            ("arcs", CpnArcDefinition),
        )
        for field_name, member_type in collections:
            values = getattr(self, field_name)
            if type(values) is not tuple or any(
                type(value) is not member_type for value in values
            ):
                raise TypeError(
                    f"{field_name} must be a tuple of {member_type.__name__}"
                )
            identities = tuple(value.identity for value in values)
            if len(set(identities)) != len(identities):
                raise ValueError(f"{field_name} identities must be unique")
            ordered_values = [(value.identity.value, value) for value in values]
            ordered_values.sort()
            object.__setattr__(
                self,
                field_name,
                tuple(item[1] for item in ordered_values),
            )
        if not isinstance(self.selection_policy, CpnSelectionPolicy):
            raise TypeError("selection_policy must be CpnSelectionPolicy")
        if type(self.control_record_types) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.control_record_types
        ):
            raise TypeError(
                "control_record_types must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )
        if len({item.identity for item in self.control_record_types}) != len(
            self.control_record_types
        ):
            raise ValueError("control-record type identities must be unique")
        ordered_record_definitions = [
            (item.identity.value, item) for item in self.control_record_types
        ]
        ordered_record_definitions.sort()
        object.__setattr__(
            self,
            "control_record_types",
            tuple(item[1] for item in ordered_record_definitions),
        )
        if type(self.transition_priority) is not tuple or any(
            type(item) is not CpnTransitionIdentity
            for item in self.transition_priority
        ):
            raise TypeError(
                "transition_priority must be a tuple of CpnTransitionIdentity"
            )
        transition_ids = tuple(item.identity for item in self.transitions)
        if len(set(self.transition_priority)) != len(self.transition_priority):
            raise ValueError("transition_priority identities must be unique")
        if set(self.transition_priority) != set(transition_ids):
            raise ValueError(
                "transition_priority must contain every transition identity "
                "exactly once"
            )
