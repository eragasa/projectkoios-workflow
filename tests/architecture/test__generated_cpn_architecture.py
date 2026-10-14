"""Architecture test for generated CPN owner documentation."""

import subprocess
import sys
from pathlib import Path

import pytest


def test__cpn_architecture_documentation__matches_semantic_owners(
    pytestconfig: pytest.Config,
) -> None:
    """Keep detailed owner documentation generated from the current source."""
    root = Path(str(pytestconfig.rootpath))
    completed = subprocess.run(
        (
            sys.executable,
            str(root / "tools/generate_cpn_architecture.py"),
            "--check",
            "--root",
            str(root),
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    # Purpose: structural mirror tests can prove that files exist while leaving
    # stale source paths or dependency text inside them. Exact generation makes
    # the documentation content part of the same checked ownership boundary.
    assert completed.returncode == 0, completed.stderr
