"""Post-hoc canonical conformance evidence for immutable child exports."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits

from .canonical import (
    WorkflowChildDefinitionExportIdentityDerivationInput,
    WorkflowChildDefinitionExportIdentityDeriver,
)
from .definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowChildExportConformanceEvidenceReference:
    """One exact canonical conformance-evidence artifact reference."""

    role_identity: str
    artifact_identity: str
    representation_profile_identity: str
    media_type_identity: str
    artifact_sha256: str
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "role_identity",
            "artifact_identity",
            "representation_profile_identity",
            "media_type_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if not (
            type(self.artifact_sha256) is str
            and len(self.artifact_sha256) == 64
            and self.artifact_sha256 == self.artifact_sha256.lower()
            and all(item in hexdigits for item in self.artifact_sha256)
        ):
            raise ValueError("artifact_sha256 must be lowercase SHA-256")
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "artifact_identity": self.artifact_identity,
            "artifact_sha256": self.artifact_sha256,
            "contract_version": str(self.contract_version),
            "media_type_identity": self.media_type_identity,
            "representation_profile_identity": (
                self.representation_profile_identity
            ),
            "role_identity": self.role_identity,
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
            "projectkoios.workflow.child-export-conformance-evidence-reference:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowChildExportEvidenceBindingIdentity:
    """Content-derived identity of one child-export evidence binding."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError(
                "child-export evidence-binding identity must be a string"
            )
        prefix = "projectkoios.workflow.child-export-evidence-binding:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError(
                "child-export evidence-binding identity has wrong domain"
            )
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "child-export evidence-binding identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class WorkflowChildExportEvidenceBinding:
    """Bind an already-identified child export to canonical evidence references."""

    child_export: WorkflowChildDefinitionExport
    evidence_references: tuple[
        WorkflowChildExportConformanceEvidenceReference, ...
    ]
    contract_version: int
    identity: WorkflowChildExportEvidenceBindingIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.child_export) is not WorkflowChildDefinitionExport:
            raise TypeError(
                "child_export must be WorkflowChildDefinitionExport"
            )
        expected_export_identity = (
            WorkflowChildDefinitionExportIdentityDeriver().execute(
                WorkflowChildDefinitionExportIdentityDerivationInput(
                    self.child_export.closure
                )
            )
        )
        if self.child_export.identity != expected_export_identity:
            raise ValueError("child_export identity does not match its closure")
        references = self.evidence_references
        if type(references) is not tuple or any(
            type(item) is not WorkflowChildExportConformanceEvidenceReference
            for item in references
        ):
            raise TypeError(
                "evidence_references must contain exact conformance references"
            )
        if not references:
            raise ValueError("evidence_references must not be empty")
        reference_identities = tuple(item.identity for item in references)
        if reference_identities != tuple(sorted(set(reference_identities))):
            raise ValueError(
                "evidence_references must be unique and identity-ordered"
            )
        roles = tuple(item.role_identity for item in references)
        if roles != tuple(sorted(set(roles))):
            raise ValueError(
                "evidence_references must have unique lexically ordered roles"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "child_export_identity": self.child_export.identity.value,
            "contract_version": str(self.contract_version),
            "evidence_reference_identities": list(reference_identities),
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
            WorkflowChildExportEvidenceBindingIdentity(
                "projectkoios.workflow.child-export-evidence-binding:0.1:"
                + sha256(encoded).hexdigest()
            ),
        )

    @property
    def child_export_identity(self) -> WorkflowChildDefinitionExportIdentity:
        """Return the exact already-derived child-export identity."""
        return self.child_export.identity
