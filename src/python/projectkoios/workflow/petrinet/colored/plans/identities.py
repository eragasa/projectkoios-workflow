"""Content identity of one complete Workflow execution plan."""

from dataclasses import dataclass
from string import hexdigits


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanIdentity:
    """Content-derived identity of complete executable semantic closure."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("execution-plan identity must be a string")
        prefix = "projectkoios.workflow.execution-plan:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("execution-plan identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "execution-plan identity must end in lowercase SHA-256"
            )
