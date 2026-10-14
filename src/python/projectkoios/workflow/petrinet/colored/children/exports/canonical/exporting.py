"""Canonical content identity derivation for child-definition exports."""

from dataclasses import dataclass
from typing import final

from ..definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportClosure,
)
from .identity import (
    WorkflowChildDefinitionExportIdentityDerivationInput,
    WorkflowChildDefinitionExportIdentityDeriver,
)


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExporterIdentity:
    """Identity of exact immutable child-export assembly semantics."""

    value: str = "projectkoios.workflow.cpn.child-definition-exporter:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportInput:
    """Complete semantic closure to assemble as one child export."""

    closure: WorkflowChildDefinitionExportClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowChildDefinitionExportClosure:
            raise TypeError(
                "closure must be WorkflowChildDefinitionExportClosure"
            )


@final
class WorkflowChildDefinitionExporter:
    """Directly assemble a child export with no post-hoc evidence cycle."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowChildDefinitionExporterIdentity:
        """Return exact exporter semantics identity."""
        return WorkflowChildDefinitionExporterIdentity()

    def execute(
        self, export_input: WorkflowChildDefinitionExportInput
    ) -> WorkflowChildDefinitionExport:
        """Derive and bind the exact content identity to one immutable closure."""
        if type(export_input) is not WorkflowChildDefinitionExportInput:
            raise TypeError(
                "export_input must be WorkflowChildDefinitionExportInput"
            )
        identity = WorkflowChildDefinitionExportIdentityDeriver().execute(
            WorkflowChildDefinitionExportIdentityDerivationInput(
                export_input.closure
            )
        )
        return WorkflowChildDefinitionExport(export_input.closure, identity)
