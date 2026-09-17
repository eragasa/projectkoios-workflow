"""Deterministic structural validation for generic colored-Petri-net state.

Validators inspect relationships among independently valid definitions,
expressions, and markings and return immutable canonically ordered findings.
Validation does not evaluate enablement, fire transitions, invoke Tasks, perform
effects, grant authority, or establish scientific validity or acceptance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .definitions import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetColorDefinition,
    ColoredPetriNetDefinition,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetTransitionDefinition,
)
from .expressions import (
    ColoredPetriNetGuardExpression,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
)
from .markings import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetMarking,
)
from .values import ColoredPetriNetColorIdentity


class ColoredPetriNetValidationIssueCode(StrEnum):
    """Stable semantic codes for v2 structural findings.

    Attributes
    ----------
    UNKNOWN_COLOR
        A referenced color is absent from the definition.
    UNKNOWN_PLACE
        An arc references a place absent from the definition.
    UNKNOWN_TRANSITION
        An arc references a transition absent from the definition.
    COLOR_NOT_ALLOWED
        A pattern, template, or token color is not admitted by its place.
    VALUE_KIND_NOT_ALLOWED
        A token value kind is not admitted by its color definition.
    UNDECLARED_BINDING_VARIABLE
        A pattern or expression references a variable outside its permitted role.
    UNBOUND_BINDING_VARIABLE
        A declared input variable has no valid consume/read binder.
    DUPLICATE_BINDING_VARIABLE
        A declared input variable has multiple valid consume/read binders.
    EXTERNAL_OUTPUT_VARIABLE_IN_GUARD
        A guard references a variable reserved for external output.
    DEFINITION_IDENTITY_MISMATCH
        A marking identifies a different definition from the supplied definition.
    PLACE_SET_MISMATCH
        A marking does not contain exactly the definition's place set.
    """

    UNKNOWN_COLOR = "unknown_color"
    UNKNOWN_PLACE = "unknown_place"
    UNKNOWN_TRANSITION = "unknown_transition"
    COLOR_NOT_ALLOWED = "color_not_allowed"
    VALUE_KIND_NOT_ALLOWED = "value_kind_not_allowed"
    UNDECLARED_BINDING_VARIABLE = "undeclared_binding_variable"
    UNBOUND_BINDING_VARIABLE = "unbound_binding_variable"
    DUPLICATE_BINDING_VARIABLE = "duplicate_binding_variable"
    EXTERNAL_OUTPUT_VARIABLE_IN_GUARD = "external_output_variable_in_guard"
    DEFINITION_IDENTITY_MISMATCH = "definition_identity_mismatch"
    PLACE_SET_MISMATCH = "place_set_mismatch"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetValidationIssue:
    """One immutable structural validation finding.

    Parameters
    ----------
    code
        Stable v2 semantic issue code.
    path
        Nonempty exact structural path from the validated root.
    related_identities
        Nonempty lexical identities stored canonically. Repeated lexical values are
        retained when distinct nominal identity classes share the same spelling.
    message
        Nonempty sanitized diagnostic with no authority or scientific meaning.

    Raises
    ------
    TypeError
        A field has the wrong semantic type or a collection is mutable.
    ValueError
        A required tuple or string is empty.
    """

    code: ColoredPetriNetValidationIssueCode
    path: tuple[str, ...]
    related_identities: tuple[str, ...]
    message: str

    def __post_init__(self) -> None:
        """Validate immutable issue state and canonicalize related identities."""
        if not isinstance(self.code, ColoredPetriNetValidationIssueCode):
            raise TypeError("code must be ColoredPetriNetValidationIssueCode")
        for field_name in ("path", "related_identities"):
            values = getattr(self, field_name)
            if type(values) is not tuple or any(
                type(item) is not str for item in values
            ):
                raise TypeError(f"{field_name} must be a tuple of strings")
            if not values or any(not item for item in values):
                raise ValueError(f"{field_name} entries must be nonempty")
        if type(self.message) is not str:
            raise TypeError("message must be a string")
        if not self.message:
            raise ValueError("message must not be empty")
        object.__setattr__(
            self, "related_identities", tuple(sorted(self.related_identities))
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetValidationResult:
    """Canonical immutable structural findings from one validation operation.

    Parameters
    ----------
    issues
        Complete findings canonicalized by path, code, related identities, and
        message. Repeated exact findings are retained when repeated malformed
        occurrences produce them.

    Raises
    ------
    TypeError
        ``issues`` is mutable or contains a wrong semantic type.
    """

    issues: tuple[ColoredPetriNetValidationIssue, ...]

    def __post_init__(self) -> None:
        """Validate and canonically order complete findings without collapsing them."""
        if type(self.issues) is not tuple or any(
            type(issue) is not ColoredPetriNetValidationIssue for issue in self.issues
        ):
            raise TypeError("issues must be a tuple of ColoredPetriNetValidationIssue")
        object.__setattr__(
            self,
            "issues",
            tuple(
                sorted(
                    self.issues,
                    key=lambda issue: (
                        issue.path,
                        issue.code.value,
                        issue.related_identities,
                        issue.message,
                    ),
                )
            ),
        )

    @property
    def is_valid(self) -> bool:
        """Whether no declared structural issue was found."""
        return not self.issues


def _issue(
    code: ColoredPetriNetValidationIssueCode,
    path: tuple[str, ...],
    identities: tuple[str, ...],
    message: str,
) -> ColoredPetriNetValidationIssue:
    """Construct one internal finding without hiding validation policy."""
    return ColoredPetriNetValidationIssue(code, path, identities, message)


def _value_variables(
    expression: ColoredPetriNetValueExpression,
) -> tuple[ColoredPetriNetBindingVariableIdentity, ...]:
    """Return the variable referenced by one closed value expression, if any."""
    if expression.kind is ColoredPetriNetValueExpressionKind.VARIABLE:
        assert expression.variable_identity is not None
        return (expression.variable_identity,)
    return ()


def _guard_variables(
    guard: ColoredPetriNetGuardExpression,
) -> tuple[ColoredPetriNetBindingVariableIdentity, ...]:
    """Return every variable reference in deterministic guard-tree order."""
    values = tuple(
        variable
        for expression in (guard.left, guard.right)
        if expression is not None
        for variable in _value_variables(expression)
    )
    nested = tuple(
        variable for operand in guard.operands for variable in _guard_variables(operand)
    )
    return values + nested


class ColoredPetriNetDefinitionValidator:
    """ActionObject for deterministic generic definition validation."""

    def execute(
        self, definition: ColoredPetriNetDefinition
    ) -> ColoredPetriNetValidationResult:
        """Return all declared cross-object definition findings.

        Parameters
        ----------
        definition
            Exact immutable generic definition to inspect.

        Returns
        -------
        ColoredPetriNetValidationResult
            Complete canonically ordered structural findings.

        Raises
        ------
        TypeError
            ``definition`` is not exactly ``ColoredPetriNetDefinition``.

        Notes
        -----
        Unknown arc place/transition references suppress dependent pattern/template
        and binder findings for that arc; the primary reference findings remain.
        """
        if type(definition) is not ColoredPetriNetDefinition:
            raise TypeError("definition must be ColoredPetriNetDefinition")
        issues: list[ColoredPetriNetValidationIssue] = []
        colors = {item.identity: item for item in definition.colors}
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}

        for place_definition in definition.places:
            for color_identity in place_definition.allowed_color_identities:
                if color_identity not in colors:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
                            (
                                "places",
                                place_definition.identity.value,
                                "allowed_colors",
                            ),
                            (place_definition.identity.value, color_identity.value),
                            "place admits an unknown color",
                        )
                    )

        for arc in definition.arcs:
            arc_path = ("arcs", arc.identity.value)
            place = places.get(arc.place_identity)
            transition = transitions.get(arc.transition_identity)
            if place is None:
                issues.append(
                    _issue(
                        ColoredPetriNetValidationIssueCode.UNKNOWN_PLACE,
                        arc_path + ("place",),
                        (arc.identity.value, arc.place_identity.value),
                        "arc references an unknown place",
                    )
                )
            if transition is None:
                issues.append(
                    _issue(
                        ColoredPetriNetValidationIssueCode.UNKNOWN_TRANSITION,
                        arc_path + ("transition",),
                        (arc.identity.value, arc.transition_identity.value),
                        "arc references an unknown transition",
                    )
                )
            if place is not None and transition is not None:
                if arc.input_inscription is not None:
                    self._validate_input_arc(arc, place, transition, colors, issues)
                if arc.output_inscription is not None:
                    self._validate_output_arc(arc, place, transition, colors, issues)

        for transition in definition.transitions:
            input_variables = set(transition.input_variable_identities)
            external_variables = set(transition.external_output_variable_identities)
            guard_variables = _guard_variables(transition.guard)
            for variable in guard_variables:
                if variable in external_variables:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
                            ("transitions", transition.identity.value, "guard"),
                            (transition.identity.value, variable.value),
                            "guard references an external-output variable",
                        )
                    )
                elif variable not in input_variables:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                            ("transitions", transition.identity.value, "guard"),
                            (transition.identity.value, variable.value),
                            "guard references an undeclared input variable",
                        )
                    )
            binders = tuple(
                pattern.variable_identity
                for arc in definition.arcs
                if arc.transition_identity == transition.identity
                and arc.place_identity in places
                and arc.input_inscription is not None
                for pattern in arc.input_inscription.patterns
                if type(pattern) is ColoredPetriNetTokenPattern
            )
            for variable in transition.input_variable_identities:
                count = binders.count(variable)
                if count == 0:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.UNBOUND_BINDING_VARIABLE,
                            ("transitions", transition.identity.value, "variables"),
                            (transition.identity.value, variable.value),
                            "declared input variable has no binding pattern",
                        )
                    )
                elif count > 1:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.DUPLICATE_BINDING_VARIABLE,
                            ("transitions", transition.identity.value, "variables"),
                            (transition.identity.value, variable.value),
                            "declared input variable has multiple binding patterns",
                        )
                    )
        return ColoredPetriNetValidationResult(tuple(issues))

    @staticmethod
    def _validate_input_arc(
        arc: ColoredPetriNetArcDefinition,
        place: ColoredPetriNetPlaceDefinition | None,
        transition: ColoredPetriNetTransitionDefinition | None,
        colors: dict[ColoredPetriNetColorIdentity, ColoredPetriNetColorDefinition],
        issues: list[ColoredPetriNetValidationIssue],
    ) -> None:
        """Append structural findings for one input arc."""
        assert arc.input_inscription is not None
        assert transition is not None
        declared = set(transition.input_variable_identities)
        for index, pattern in enumerate(arc.input_inscription.patterns):
            path = ("arcs", arc.identity.value, "input_patterns", str(index))
            admitted = pattern.allowed_color_identities
            for color_identity in admitted:
                if color_identity not in colors:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
                            path + ("colors",),
                            (arc.identity.value, color_identity.value),
                            "input pattern references an unknown color",
                        )
                    )
                elif (
                    place is not None
                    and color_identity not in place.allowed_color_identities
                ):
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.COLOR_NOT_ALLOWED,
                            path + ("colors",),
                            (place.identity.value, color_identity.value),
                            "input pattern color is not admitted by the place",
                        )
                    )
            if type(pattern) is ColoredPetriNetTokenPattern and (
                pattern.variable_identity not in declared
            ):
                issues.append(
                    _issue(
                        ColoredPetriNetValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                        path + ("variable",),
                        (
                            arc.transition_identity.value,
                            pattern.variable_identity.value,
                        ),
                        "input pattern binds an undeclared variable",
                    )
                )

    @staticmethod
    def _validate_output_arc(
        arc: ColoredPetriNetArcDefinition,
        place: ColoredPetriNetPlaceDefinition | None,
        transition: ColoredPetriNetTransitionDefinition | None,
        colors: dict[ColoredPetriNetColorIdentity, ColoredPetriNetColorDefinition],
        issues: list[ColoredPetriNetValidationIssue],
    ) -> None:
        """Append structural findings for one output arc."""
        assert arc.output_inscription is not None
        assert transition is not None
        declared = set(transition.input_variable_identities) | set(
            transition.external_output_variable_identities
        )
        for index, template in enumerate(arc.output_inscription.templates):
            path = ("arcs", arc.identity.value, "output_templates", str(index))
            if template.color_identity not in colors:
                issues.append(
                    _issue(
                        ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
                        path + ("color",),
                        (arc.identity.value, template.color_identity.value),
                        "output template references an unknown color",
                    )
                )
            elif (
                place is not None
                and template.color_identity not in place.allowed_color_identities
            ):
                issues.append(
                    _issue(
                        ColoredPetriNetValidationIssueCode.COLOR_NOT_ALLOWED,
                        path + ("color",),
                        (place.identity.value, template.color_identity.value),
                        "output template color is not admitted by the place",
                    )
                )
            expressions = (template.value_expression,) + (
                ()
                if template.token_identity_expression is None
                else (template.token_identity_expression,)
            )
            for expression in expressions:
                for variable in _value_variables(expression):
                    if variable not in declared:
                        issues.append(
                            _issue(
                                ColoredPetriNetValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                                path + ("variable",),
                                (arc.transition_identity.value, variable.value),
                                "output template references an undeclared variable",
                            )
                        )


class ColoredPetriNetMarkingValidator:
    """ActionObject for definition-relative generic marking validation."""

    def execute(
        self,
        definition: ColoredPetriNetDefinition,
        marking: ColoredPetriNetMarking,
    ) -> ColoredPetriNetValidationResult:
        """Return all declared definition-relative marking findings.

        Parameters
        ----------
        definition
            Exact immutable generic definition providing place/color contracts.
        marking
            Exact immutable semantic marking to inspect.

        Returns
        -------
        ColoredPetriNetValidationResult
            Complete canonically ordered structural findings.

        Raises
        ------
        TypeError
            Either argument has the wrong exact nominal type.
        """
        if type(definition) is not ColoredPetriNetDefinition:
            raise TypeError("definition must be ColoredPetriNetDefinition")
        if type(marking) is not ColoredPetriNetMarking:
            raise TypeError("marking must be ColoredPetriNetMarking")
        issues: list[ColoredPetriNetValidationIssue] = []
        places = {item.identity: item for item in definition.places}
        colors = {item.identity: item for item in definition.colors}
        if marking.definition_identity != definition.identity:
            issues.append(
                _issue(
                    ColoredPetriNetValidationIssueCode.DEFINITION_IDENTITY_MISMATCH,
                    ("marking", "definition_identity"),
                    (marking.definition_identity.value, definition.identity.value),
                    "marking and supplied definition identities differ",
                )
            )
        marking_places = {item.place_identity for item in marking.places}
        definition_places = set(places)
        if marking_places != definition_places:
            issues.append(
                _issue(
                    ColoredPetriNetValidationIssueCode.PLACE_SET_MISMATCH,
                    ("marking", "places"),
                    tuple(item.value for item in marking_places ^ definition_places),
                    "marking place set differs from definition place set",
                )
            )
        for place_marking in marking.places:
            place = places.get(place_marking.place_identity)
            for index, token in enumerate(place_marking.tokens):
                path = (
                    "marking",
                    "places",
                    place_marking.place_identity.value,
                    "tokens",
                    str(index),
                )
                color = colors.get(token.color_identity)
                if color is None:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
                            path + ("color",),
                            (token.color_identity.value,),
                            "token references an unknown color",
                        )
                    )
                    continue
                if (
                    place is not None
                    and token.color_identity not in place.allowed_color_identities
                ):
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.COLOR_NOT_ALLOWED,
                            path + ("color",),
                            (place.identity.value, token.color_identity.value),
                            "token color is not admitted by the place",
                        )
                    )
                if token.value.kind not in color.allowed_value_kinds:
                    issues.append(
                        _issue(
                            ColoredPetriNetValidationIssueCode.VALUE_KIND_NOT_ALLOWED,
                            path + ("value_kind",),
                            (token.color_identity.value, token.value.kind.value),
                            "token value kind is not admitted by its color",
                        )
                    )
        return ColoredPetriNetValidationResult(tuple(issues))
