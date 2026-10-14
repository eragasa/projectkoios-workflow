"""Architecture test for the generated source-of-truth baseline."""

import subprocess
import sys
from pathlib import Path

import pytest


def test__architecture_baseline__matches_source_graph(
    pytestconfig: pytest.Config,
) -> None:
    """Reject hand-maintained observations that have drifted from source."""
    root = Path(str(pytestconfig.rootpath))
    completed = subprocess.run(
        (
            sys.executable,
            str(root / "tools/generate_workflow_architecture.py"),
            "--check",
            "--root",
            str(root),
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    # Purpose: human documents should explain architectural intent, while the
    # volatile module inventory and dependency counts come from the same graph
    # that CI enforces. This prevents a plausible but obsolete baseline.
    assert completed.returncode == 0, completed.stderr
