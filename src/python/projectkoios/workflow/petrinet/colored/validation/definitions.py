"""Complete flat CPN definition validation."""

from __future__ import annotations

from dataclasses import dataclass

from ..control.records.type_graph import (
    CpnControlRecordTypeGraphValidationInput,
    CpnControlRecordTypeGraphValidator,
)
from ..definitions import (
    CpnArcDefinition,
    CpnDefinition,
)
from ..expressions.collection import (
    CpnExpressionVariableCollectionInput,
    CpnExpressionVariableCollector,
    CpnGuardVariableCollectionInput,
    CpnGuardVariableCollector,
)
from ..expressions.errors import CpnExpressionOperationError
from ..expressions.grammar import CpnTokenPattern
from ..expressions.validation import (
    CpnExpressionBoundsValidationInput,
    CpnExpressionBoundsValidator,
)
from .findings import (
    CpnValidationIssue,
    CpnValidationIssueCode,
    CpnValidationResult,
)


@dataclass(frozen=True, slots=True)
class CpnInputArcValidationRequest:
    """Complete owner definition and exact input arc to validate."""

    definition: CpnDefinition
    arc: CpnArcDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.arc) is not CpnArcDefinition:
            raise TypeError("arc must be CpnArcDefinition")


@dataclass(frozen=True, slots=True)
class CpnInputArcValidationResponse:
    """Named response from one input-arc validation operation."""

    result: CpnValidationResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnValidationResult:
            raise TypeError("result must be CpnValidationResult")


@dataclass(frozen=True, slots=True)
class CpnInputArcValidatorIdentity:
    """Identity of exact input-arc validation semantics."""

    value: str = "projectkoios.workflow.cpn.input-arc-validator:0.1"


class CpnInputArcValidator:
    """Validate one input arc without mutating a caller-owned issue list."""

    __slots__ = ()

    @property
    def identity(self) -> CpnInputArcValidatorIdentity:
        """Return exact input-arc validation semantics identity."""
        return CpnInputArcValidatorIdentity()

    def execute(
        self, request: CpnInputArcValidationRequest
    ) -> CpnInputArcValidationResponse:
        """Return named structural findings for one input arc."""
        if type(request) is not CpnInputArcValidationRequest:
            raise TypeError("request must be CpnInputArcValidationRequest")
        definition = request.definition
        arc = request.arc
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}
        colors = {item.identity: item for item in definition.colors}
        place = places.get(arc.place_identity)
        transition = transitions.get(arc.transition_identity)
        if arc.input_inscription is None or transition is None:
            return CpnInputArcValidationResponse(CpnValidationResult(()))
        issues: list[CpnValidationIssue] = []
        declared = set(transition.input_variable_identities)
        for index, pattern in enumerate(arc.input_inscription.patterns):
            path = ("arcs", arc.identity.value, "input_patterns", str(index))
            for color_identity in pattern.allowed_color_identities:
                if color_identity not in colors:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNKNOWN_COLOR,
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
                        CpnValidationIssue(
                            CpnValidationIssueCode.COLOR_NOT_ALLOWED,
                            path + ("colors",),
                            (place.identity.value, color_identity.value),
                            "input pattern color is not admitted by the place",
                        )
                    )
            if (
                type(pattern) is CpnTokenPattern
                and pattern.variable_identity not in declared
            ):
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                        path + ("variable",),
                        (
                            arc.transition_identity.value,
                            pattern.variable_identity.value,
                        ),
                        "input pattern binds an undeclared variable",
                    )
                )
        return CpnInputArcValidationResponse(CpnValidationResult(tuple(issues)))


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidationRequest:
    """Complete owner definition and exact output arc to validate."""

    definition: CpnDefinition
    arc: CpnArcDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.arc) is not CpnArcDefinition:
            raise TypeError("arc must be CpnArcDefinition")


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidationResponse:
    """Named response from one output-arc validation operation."""

    result: CpnValidationResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnValidationResult:
            raise TypeError("result must be CpnValidationResult")


@dataclass(frozen=True, slots=True)
class CpnOutputArcValidatorIdentity:
    """Identity of exact output-arc validation semantics."""

    value: str = "projectkoios.workflow.cpn.output-arc-validator:0.1"


class CpnOutputArcValidator:
    """Validate one output arc without mutating caller-owned state."""

    __slots__ = ()

    @property
    def identity(self) -> CpnOutputArcValidatorIdentity:
        """Return exact output-arc validation semantics identity."""
        return CpnOutputArcValidatorIdentity()

    def execute(
        self, request: CpnOutputArcValidationRequest
    ) -> CpnOutputArcValidationResponse:
        """Return named structural findings for one output arc."""
        if type(request) is not CpnOutputArcValidationRequest:
            raise TypeError("request must be CpnOutputArcValidationRequest")
        definition = request.definition
        arc = request.arc
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}
        colors = {item.identity: item for item in definition.colors}
        place = places.get(arc.place_identity)
        transition = transitions.get(arc.transition_identity)
        if arc.output_inscription is None or transition is None:
            return CpnOutputArcValidationResponse(CpnValidationResult(()))
        issues: list[CpnValidationIssue] = []
        declared = set(transition.input_variable_identities) | set(
            transition.external_output_variable_identities
        )
        for index, template in enumerate(arc.output_inscription.templates):
            path = ("arcs", arc.identity.value, "output_templates", str(index))
            if template.color_identity not in colors:
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNKNOWN_COLOR,
                        path + ("color",),
                        (arc.identity.value, template.color_identity.value),
                        "output template references an unknown color",
                    )
                )
            elif (
                place is not None
                and template.color_identity
                not in place.allowed_color_identities
            ):
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.COLOR_NOT_ALLOWED,
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
                try:
                    variables = (
                        CpnExpressionVariableCollector()
                        .execute(
                            CpnExpressionVariableCollectionInput(expression)
                        )
                        .variable_identities
                    )
                except CpnExpressionOperationError as exc:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.INVALID_VALUE_EXPRESSION,
                            path + ("expression",),
                            (arc.transition_identity.value, exc.code.value),
                            exc.diagnostic,
                        )
                    )
                    continue
                for variable in variables:
                    if variable not in declared:
                        issues.append(
                            CpnValidationIssue(
                                CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
                                path + ("variable",),
                                (arc.transition_identity.value, variable.value),
                                "output template references an undeclared variable",
                            )
                        )
        return CpnOutputArcValidationResponse(
            CpnValidationResult(tuple(issues))
        )


@dataclass(frozen=True, slots=True)
class CpnDefinitionValidationRequest:
    """Complete immutable definition-validation request."""

    definition: CpnDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")


@dataclass(frozen=True, slots=True)
class CpnDefinitionValidatorIdentity:
    """Identity of exact generic definition-validation semantics."""

    value: str = "projectkoios.workflow.cpn.definition-validator:0.1"


class CpnDefinitionValidator:
    """ActionObject for deterministic generic definition validation."""

    __slots__ = ()

    @property
    def identity(self) -> CpnDefinitionValidatorIdentity:
        """Return exact definition-validation semantics identity."""
        return CpnDefinitionValidatorIdentity()

    def execute(
        self, request: CpnDefinitionValidationRequest
    ) -> CpnValidationResult:
        """Return all declared cross-object definition findings.

        Parameters
        ----------
        definition
            Exact immutable generic definition to inspect.

        Returns
        -------
        CpnValidationResult
            Complete canonically ordered structural findings.

        Raises
        ------
        TypeError
            ``definition`` is not exactly ``CpnDefinition``.

        Notes
        -----
        Unknown arc place/transition references suppress dependent pattern/template
        and binder findings for that arc; the primary reference findings remain.
        """
        if type(request) is not CpnDefinitionValidationRequest:
            raise TypeError("request must be CpnDefinitionValidationRequest")
        definition = request.definition
        issues: list[CpnValidationIssue] = []
        colors = {item.identity: item for item in definition.colors}
        places = {item.identity: item for item in definition.places}
        transitions = {item.identity: item for item in definition.transitions}
        record_types = {
            item.identity: item for item in definition.control_record_types
        }
        record_graph = CpnControlRecordTypeGraphValidator().execute(
            CpnControlRecordTypeGraphValidationInput(
                definition.control_record_types
            )
        )
        for record_issue in record_graph.issues:
            issues.append(
                CpnValidationIssue(
                    CpnValidationIssueCode.INVALID_CONTROL_RECORD_SCHEMA,
                    record_issue.path,
                    (record_issue.code.value,),
                    record_issue.message,
                )
            )
        for color in definition.colors:
            for (
                record_type_identity
            ) in color.allowed_control_record_type_identities:
                if record_type_identity not in record_types:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNKNOWN_CONTROL_RECORD_TYPE,
                            (
                                "colors",
                                color.identity.value,
                                "control_record_types",
                            ),
                            (color.identity.value, record_type_identity.value),
                            "color admits an unknown control-record type",
                        )
                    )

        for place_definition in definition.places:
            for color_identity in place_definition.allowed_color_identities:
                if color_identity not in colors:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNKNOWN_COLOR,
                            (
                                "places",
                                place_definition.identity.value,
                                "allowed_colors",
                            ),
                            (
                                place_definition.identity.value,
                                color_identity.value,
                            ),
                            "place admits an unknown color",
                        )
                    )

        for arc in definition.arcs:
            arc_path = ("arcs", arc.identity.value)
            place = places.get(arc.place_identity)
            transition = transitions.get(arc.transition_identity)
            if place is None:
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNKNOWN_PLACE,
                        arc_path + ("place",),
                        (arc.identity.value, arc.place_identity.value),
                        "arc references an unknown place",
                    )
                )
            if transition is None:
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.UNKNOWN_TRANSITION,
                        arc_path + ("transition",),
                        (arc.identity.value, arc.transition_identity.value),
                        "arc references an unknown transition",
                    )
                )
            if place is not None and transition is not None:
                if arc.input_inscription is not None:
                    input_response = CpnInputArcValidator().execute(
                        CpnInputArcValidationRequest(definition, arc)
                    )
                    issues.extend(input_response.result.issues)
                if arc.output_inscription is not None:
                    output_response = CpnOutputArcValidator().execute(
                        CpnOutputArcValidationRequest(definition, arc)
                    )
                    issues.extend(output_response.result.issues)

        for transition in definition.transitions:
            input_variables = set(transition.input_variable_identities)
            try:
                guard_variables = (
                    CpnGuardVariableCollector()
                    .execute(CpnGuardVariableCollectionInput(transition.guard))
                    .variable_identities
                )
            except CpnExpressionOperationError:
                guard_variables = ()
            output_expressions = tuple(
                expression
                for arc in definition.arcs
                if arc.transition_identity == transition.identity
                and arc.output_inscription is not None
                for template in arc.output_inscription.templates
                for expression in (
                    (template.value_expression,)
                    if template.token_identity_expression is None
                    else (
                        template.value_expression,
                        template.token_identity_expression,
                    )
                )
            )
            bounds_result = CpnExpressionBoundsValidator().execute(
                CpnExpressionBoundsValidationInput(
                    transition.guard,
                    output_expressions,
                    definition.control_record_types,
                )
            )
            for expression_issue in bounds_result.issues:
                issues.append(
                    CpnValidationIssue(
                        CpnValidationIssueCode.INVALID_VALUE_EXPRESSION,
                        ("transitions", transition.identity.value)
                        + expression_issue.path,
                        (
                            transition.identity.value,
                            expression_issue.code.value,
                        ),
                        expression_issue.diagnostic,
                    )
                )
            external_variables = set(
                transition.external_output_variable_identities
            )
            for variable in guard_variables:
                if variable in external_variables:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
                            ("transitions", transition.identity.value, "guard"),
                            (transition.identity.value, variable.value),
                            "guard references an external-output variable",
                        )
                    )
                elif variable not in input_variables:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
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
                if type(pattern) is CpnTokenPattern
            )
            for variable in transition.input_variable_identities:
                count = binders.count(variable)
                if count == 0:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNBOUND_BINDING_VARIABLE,
                            (
                                "transitions",
                                transition.identity.value,
                                "variables",
                            ),
                            (transition.identity.value, variable.value),
                            "declared input variable has no binding pattern",
                        )
                    )
                elif count > 1:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.DUPLICATE_BINDING_VARIABLE,
                            (
                                "transitions",
                                transition.identity.value,
                                "variables",
                            ),
                            (transition.identity.value, variable.value),
                            "declared input variable has multiple binding patterns",
                        )
                    )
        return CpnValidationResult(tuple(issues))
