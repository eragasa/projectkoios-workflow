"""Immutable execution-plan closure, construction, and identity."""

from dataclasses import dataclass
from typing import final

from .definition import WorkflowExecutionPlanClosure
from .identities import WorkflowExecutionPlanIdentity
from .identity import (
    WorkflowExecutionPlanIdentityDerivationInput,
    WorkflowExecutionPlanIdentityDeriver,
)


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlan:
    """One complete immutable plan closure and content identity."""

    closure: WorkflowExecutionPlanClosure
    identity: WorkflowExecutionPlanIdentity
    canonical_sha256: str

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowExecutionPlanClosure:
            raise TypeError("closure must be WorkflowExecutionPlanClosure")
        if type(self.identity) is not WorkflowExecutionPlanIdentity:
            raise TypeError("identity must be WorkflowExecutionPlanIdentity")
        if self.canonical_sha256 != self.identity.value.rsplit(":", 1)[-1]:
            raise ValueError(
                "canonical_sha256 must equal the execution-plan identity digest"
            )
        derived = WorkflowExecutionPlanIdentityDeriver().execute(
            WorkflowExecutionPlanIdentityDerivationInput(self.closure)
        )
        if derived != self.identity:
            raise ValueError(
                "execution-plan identity does not match its closure"
            )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanCompilerIdentity:
    """Identity of exact immutable execution-plan assembly semantics."""

    value: str = "projectkoios.workflow.cpn.execution-plan-compiler:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanCompilationInput:
    """Complete semantic closure to compile as one execution plan."""

    closure: WorkflowExecutionPlanClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowExecutionPlanClosure:
            raise TypeError("closure must be WorkflowExecutionPlanClosure")


@final
class WorkflowExecutionPlanCompiler:
    """Directly assemble an immutable identity-closed execution plan."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowExecutionPlanCompilerIdentity:
        """Return exact plan assembly semantics identity."""
        return WorkflowExecutionPlanCompilerIdentity()

    def execute(
        self, compilation_input: WorkflowExecutionPlanCompilationInput
    ) -> WorkflowExecutionPlan:
        """Derive and retain the exact plan identity and canonical digest."""
        if type(compilation_input) is not WorkflowExecutionPlanCompilationInput:
            raise TypeError(
                "compilation_input must be WorkflowExecutionPlanCompilationInput"
            )
        identity = WorkflowExecutionPlanIdentityDeriver().execute(
            WorkflowExecutionPlanIdentityDerivationInput(
                compilation_input.closure
            )
        )
        return WorkflowExecutionPlan(
            compilation_input.closure,
            identity,
            identity.value.rsplit(":", 1)[-1],
        )
