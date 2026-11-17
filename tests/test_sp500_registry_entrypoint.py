"""The earnings workflow runs the registry script without pip-installing Compound."""
from pathlib import Path
import subprocess
import sys


def test_registry_cli_imports_normaliser_without_editable_install():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-S", str(root / "scripts/sp500_registry.py"), "--help"],
        cwd=root, capture_output=True, text=True, timeout=20, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--output" in result.stdout
