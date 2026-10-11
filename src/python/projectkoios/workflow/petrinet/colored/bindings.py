"""Immutable ordered CPN transition bindings."""

from dataclasses import dataclass

from .definitions import CpnTransitionIdentity
from .expressions.grammar import CpnBindingVariableIdentity
from .values import CpnValue


@dataclass(frozen=True, slots=True)
class CpnBindingAssignment:
    """Association of one definition-owned variable with one generic value.

    Parameters
    ----------
    variable_identity
        Nominal identity of the bound variable.
    value
        Exact immutable generic value assigned to the variable.

    Raises
    ------
    TypeError
        A field does not have its exact owner-local nominal type.
    """

    variable_identity: CpnBindingVariableIdentity
    value: CpnValue

    def __post_init__(self) -> None:
        """Validate exact nominal assignment components."""
        if type(self.variable_identity) is not CpnBindingVariableIdentity:
            raise TypeError(
                "variable_identity must be CpnBindingVariableIdentity"
            )
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@dataclass(frozen=True, slots=True)
class CpnBinding:
    """One immutable ordered variable/value binding for a transition.

    Parameters
    ----------
    transition_identity
        Nominal identity of the transition for which values are bound.
    assignments
        Complete variable/value assignments in the owning definition's declared
        variable order. This DataObject preserves that order and requires unique
        variable identities; it does not infer or lexically reorder policy.

    Raises
    ------
    TypeError
        A field has the wrong nominal type or ``assignments`` is mutable.
    ValueError
        A variable identity occurs more than once.
    """

    transition_identity: CpnTransitionIdentity
    assignments: tuple[CpnBindingAssignment, ...]

    def __post_init__(self) -> None:
        """Validate the intrinsic ordered-binding structure."""
        if type(self.transition_identity) is not CpnTransitionIdentity:
            raise TypeError("transition_identity must be CpnTransitionIdentity")
        if type(self.assignments) is not tuple or any(
            type(item) is not CpnBindingAssignment for item in self.assignments
        ):
            raise TypeError(
                "assignments must be a tuple of CpnBindingAssignment"
            )
        variables = tuple(item.variable_identity for item in self.assignments)
        if len(set(variables)) != len(variables):
            raise ValueError("binding variable identities must be unique")
