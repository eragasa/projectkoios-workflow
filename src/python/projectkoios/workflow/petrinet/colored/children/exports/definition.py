"""Complete immutable child-definition export records."""

from dataclasses import dataclass
from string import hexdigits

from ..interfaces import WorkflowChildInterface
from ...plans.identities import WorkflowExecutionPlanIdentity
from ...profiles.definition import WorkflowCpnExecutionProfileIdentity


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportIdentity:
    """Content-derived identity of one exact child definition export."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("child-export identity must be a string")
        prefix = "projectkoios.workflow.child-definition-export:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("child-export identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "child-export identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportClosure:
    """Complete owner-neutral semantic closure of one child export."""

    owner_identity: str
    workflow_family_identity: str
    source_definition_identity: str
    source_definition_contract_version: int
    execution_plan_identity: WorkflowExecutionPlanIdentity
    execution_plan_sha256: str
    nominal_definition_identity: str
    canonical_definition_identity: str
    canonical_definition_representation_profile_identity: str
    canonical_definition_sha256: str
    cpn_execution_profile_identity: WorkflowCpnExecutionProfileIdentity
    initial_marking_constructor_identity: str
    interface: WorkflowChildInterface
    compiler_implementation_identity: str
    compiler_version_identity: str
    exporter_implementation_identity: str
    exporter_version_identity: str
    source_revision_identity: str
    contract_version: int

    def __post_init__(self) -> None:
        for name in (
            "owner_identity",
            "workflow_family_identity",
            "source_definition_identity",
            "nominal_definition_identity",
            "canonical_definition_identity",
            "canonical_definition_representation_profile_identity",
            "initial_marking_constructor_identity",
            "compiler_implementation_identity",
            "compiler_version_identity",
            "exporter_implementation_identity",
            "exporter_version_identity",
            "source_revision_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        for name in ("source_definition_contract_version", "contract_version"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise TypeError(f"{name} must be a positive integer")
        if (
            type(self.execution_plan_identity)
            is not WorkflowExecutionPlanIdentity
        ):
            raise TypeError(
                "execution_plan_identity must be WorkflowExecutionPlanIdentity"
            )
        if (
            type(self.cpn_execution_profile_identity)
            is not WorkflowCpnExecutionProfileIdentity
        ):
            raise TypeError(
                "cpn_execution_profile_identity must be WorkflowCpnExecutionProfileIdentity"
            )
        if type(self.interface) is not WorkflowChildInterface:
            raise TypeError("interface must be WorkflowChildInterface")
        for name in ("execution_plan_sha256", "canonical_definition_sha256"):
            value = getattr(self, name)
            if not (
                type(value) is str
                and len(value) == 64
                and value == value.lower()
                and all(item in hexdigits for item in value)
            ):
                raise ValueError(f"{name} must be lowercase SHA-256")
        if (
            self.execution_plan_sha256
            != self.execution_plan_identity.value.rsplit(":", 1)[-1]
        ):
            raise ValueError(
                "execution_plan_sha256 must equal the execution-plan identity digest"
            )


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExport:
    """One immutable child export and its content-derived identity."""

    closure: WorkflowChildDefinitionExportClosure
    identity: WorkflowChildDefinitionExportIdentity

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowChildDefinitionExportClosure:
            raise TypeError(
                "closure must be WorkflowChildDefinitionExportClosure"
            )
        if type(self.identity) is not WorkflowChildDefinitionExportIdentity:
            raise TypeError(
                "identity must be WorkflowChildDefinitionExportIdentity"
            )
