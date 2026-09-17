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

from .expressions import (
    ColoredPetriNetGuardExpression,
    ColoredPetriNetInputInscription,
    ColoredPetriNetOutputInscription,
)
from .markings import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetTransitionIdentity,
)
from .values import ColoredPetriNetColorIdentity, ColoredPetriNetValueKind


class ColoredPetriNetSelectionPolicy(StrEnum):
    """Definition-owned permission for binding selection.

    ``DETERMINISTIC_ONLY`` permits only canonical default selection.
    ``DIRECTED_ALLOWED`` additionally permits an explicit identity-bound directive.
    """

    DETERMINISTIC_ONLY = "deterministic_only"
    DIRECTED_ALLOWED = "directed_allowed"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetArcIdentity:
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
class ColoredPetriNetColorDefinition:
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

    identity: ColoredPetriNetColorIdentity
    allowed_value_kinds: tuple[ColoredPetriNetValueKind, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned admitted-kind set."""
        if type(self.identity) is not ColoredPetriNetColorIdentity:
            raise TypeError("identity must be ColoredPetriNetColorIdentity")
        if type(self.allowed_value_kinds) is not tuple or any(
            not isinstance(kind, ColoredPetriNetValueKind)
            for kind in self.allowed_value_kinds
        ):
            raise TypeError(
                "allowed_value_kinds must be a tuple of ColoredPetriNetValueKind"
            )
        if not self.allowed_value_kinds:
            raise ValueError("allowed_value_kinds must not be empty")
        if len(set(self.allowed_value_kinds)) != len(self.allowed_value_kinds):
            raise ValueError("allowed_value_kinds must be unique")
        object.__setattr__(
            self,
            "allowed_value_kinds",
            tuple(sorted(self.allowed_value_kinds, key=lambda kind: kind.value)),
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetPlaceDefinition:
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

    identity: ColoredPetriNetPlaceIdentity
    allowed_color_identities: tuple[ColoredPetriNetColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the owned admitted-color set."""
        if type(self.identity) is not ColoredPetriNetPlaceIdentity:
            raise TypeError("identity must be ColoredPetriNetPlaceIdentity")
        if type(self.allowed_color_identities) is not tuple or any(
            type(color) is not ColoredPetriNetColorIdentity
            for color in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of "
                "ColoredPetriNetColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(sorted(self.allowed_color_identities, key=lambda item: item.value)),
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTransitionDefinition:
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

    identity: ColoredPetriNetTransitionIdentity
    input_variable_identities: tuple[ColoredPetriNetBindingVariableIdentity, ...]
    external_output_variable_identities: tuple[
        ColoredPetriNetBindingVariableIdentity, ...
    ]
    guard: ColoredPetriNetGuardExpression

    def __post_init__(self) -> None:
        """Validate intrinsic transition fields while preserving variable order."""
        if type(self.identity) is not ColoredPetriNetTransitionIdentity:
            raise TypeError("identity must be ColoredPetriNetTransitionIdentity")
        for field_name in (
            "input_variable_identities",
            "external_output_variable_identities",
        ):
            variables = getattr(self, field_name)
            if type(variables) is not tuple or any(
                type(item) is not ColoredPetriNetBindingVariableIdentity
                for item in variables
            ):
                raise TypeError(
                    f"{field_name} must be a tuple of "
                    "ColoredPetriNetBindingVariableIdentity"
                )
            if len(set(variables)) != len(variables):
                raise ValueError(f"{field_name} must be unique")
        if set(self.input_variable_identities) & set(
            self.external_output_variable_identities
        ):
            raise ValueError("input and external-output variables must be disjoint")
        if type(self.guard) is not ColoredPetriNetGuardExpression:
            raise TypeError("guard must be ColoredPetriNetGuardExpression")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetArcDefinition:
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

    identity: ColoredPetriNetArcIdentity
    place_identity: ColoredPetriNetPlaceIdentity
    transition_identity: ColoredPetriNetTransitionIdentity
    input_inscription: ColoredPetriNetInputInscription | None = None
    output_inscription: ColoredPetriNetOutputInscription | None = None

    def __post_init__(self) -> None:
        """Validate nominal references and exact inscription discrimination."""
        if type(self.identity) is not ColoredPetriNetArcIdentity:
            raise TypeError("identity must be ColoredPetriNetArcIdentity")
        if type(self.place_identity) is not ColoredPetriNetPlaceIdentity:
            raise TypeError("place_identity must be ColoredPetriNetPlaceIdentity")
        if type(self.transition_identity) is not ColoredPetriNetTransitionIdentity:
            raise TypeError(
                "transition_identity must be ColoredPetriNetTransitionIdentity"
            )
        if self.input_inscription is not None and (
            type(self.input_inscription) is not ColoredPetriNetInputInscription
        ):
            raise TypeError(
                "input_inscription must be ColoredPetriNetInputInscription or None"
            )
        if self.output_inscription is not None and (
            type(self.output_inscription) is not ColoredPetriNetOutputInscription
        ):
            raise TypeError(
                "output_inscription must be ColoredPetriNetOutputInscription or None"
            )
        if (self.input_inscription is None) == (self.output_inscription is None):
            raise ValueError("exactly one arc inscription variant must be present")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetDefinition:
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
    and semantic compatibility belong to ``ColoredPetriNetDefinitionValidator``.
    """

    identity: ColoredPetriNetDefinitionIdentity
    colors: tuple[ColoredPetriNetColorDefinition, ...]
    places: tuple[ColoredPetriNetPlaceDefinition, ...]
    transitions: tuple[ColoredPetriNetTransitionDefinition, ...]
    arcs: tuple[ColoredPetriNetArcDefinition, ...]
    transition_priority: tuple[ColoredPetriNetTransitionIdentity, ...]
    selection_policy: ColoredPetriNetSelectionPolicy = (
        ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY
    )

    def __post_init__(self) -> None:
        """Validate intrinsic collections, canonicalize them, and close priority."""
        if type(self.identity) is not ColoredPetriNetDefinitionIdentity:
            raise TypeError("identity must be ColoredPetriNetDefinitionIdentity")
        collections = (
            ("colors", ColoredPetriNetColorDefinition),
            ("places", ColoredPetriNetPlaceDefinition),
            ("transitions", ColoredPetriNetTransitionDefinition),
            ("arcs", ColoredPetriNetArcDefinition),
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
            object.__setattr__(
                self,
                field_name,
                tuple(sorted(values, key=lambda value: value.identity.value)),
            )
        if not isinstance(self.selection_policy, ColoredPetriNetSelectionPolicy):
            raise TypeError("selection_policy must be ColoredPetriNetSelectionPolicy")
        if type(self.transition_priority) is not tuple or any(
            type(item) is not ColoredPetriNetTransitionIdentity
            for item in self.transition_priority
        ):
            raise TypeError(
                "transition_priority must be a tuple of "
                "ColoredPetriNetTransitionIdentity"
            )
        transition_ids = tuple(item.identity for item in self.transitions)
        if len(set(self.transition_priority)) != len(self.transition_priority):
            raise ValueError("transition_priority identities must be unique")
        if set(self.transition_priority) != set(transition_ids):
            raise ValueError(
                "transition_priority must contain every transition identity "
                "exactly once"
            )
