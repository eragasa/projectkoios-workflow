from __future__ import annotations

from pathlib import Path

_ARCHITECTURE_ROOT = Path(__file__).parents[1] / "docs" / "architecture"
_REQUIRED_DOCUMENTS = frozenset(
    {"index.md", "schematic.md", "implementation.md"}
)
_MINIMUM_DOCUMENT_LENGTH = 200
_ISSUE_ROOT = _ARCHITECTURE_ROOT / "projectkoios" / "workflow" / "issues"
_ISSUE_FIELDS = (
    "- **Kind:**",
    "- **Status:**",
    "- **Workflow-local scope:**",
    "- **Authoritative owner:**",
    "## Problem or question",
    "## Current evidence",
    "## Consequence",
    "## Alternatives and recommendation",
    "## Resolution gate",
    "## Affected architecture",
)


def _architecture_directories() -> tuple[Path, ...]:
    return (
        _ARCHITECTURE_ROOT,
        *tuple(
            sorted(
                path for path in _ARCHITECTURE_ROOT.rglob("*") if path.is_dir()
            )
        ),
    )


def test__every_architecture_level_has_the_required_documents() -> None:
    assert _ARCHITECTURE_ROOT.is_dir()
    for directory in _architecture_directories():
        names = frozenset(
            path.name for path in directory.iterdir() if path.is_file()
        )
        assert _REQUIRED_DOCUMENTS <= names, directory.relative_to(
            _ARCHITECTURE_ROOT
        )


def test__architecture_documents_state_local_responsibility() -> None:
    for directory in _architecture_directories():
        for name in sorted(_REQUIRED_DOCUMENTS):
            document = directory / name
            content = document.read_text(encoding="utf-8")
            assert len(content) >= _MINIMUM_DOCUMENT_LENGTH, document
            assert "## Responsibility" in content, document
            assert _has_explanatory_sentence(content), document


def test__workflow_issue_records_are_stable_and_complete() -> None:
    issues = tuple(sorted(_ISSUE_ROOT.glob("WF-ISSUE-[0-9][0-9][0-9][0-9].md")))
    assert issues
    for issue in issues:
        content = issue.read_text(encoding="utf-8")
        assert content.startswith(f"# {issue.stem} — "), issue
        for field in _ISSUE_FIELDS:
            assert field in content, (issue, field)
        assert "**Assignee:**" not in content, issue
        assert "**ETA:**" not in content, issue


def _has_explanatory_sentence(content: str) -> bool:
    """Reject documents that contain only headings, links, or lists."""

    in_fence = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if (
            in_fence
            or not line
            or line.startswith(("#", "-", "*", "[", "|", ">"))
        ):
            continue
        if len(line) >= 40 and any(mark in line for mark in (". ", ".", ":")):
            return True
    return False
