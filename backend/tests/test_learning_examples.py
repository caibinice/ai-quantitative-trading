from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = [
    "01_python_bridge.py",
    "02_pandas_timeseries.py",
    "03_signal_delay.py",
    "04_sentiment_factor.py",
    "05_walk_forward.py",
]


@pytest.mark.parametrize("example", EXAMPLES)
def test_learning_example_runs(example: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "learning" / "examples" / example)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert "DEMO_OK" in result.stdout
