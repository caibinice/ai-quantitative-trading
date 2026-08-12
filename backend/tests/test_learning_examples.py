from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = [
    "00_kline_basics.py",
    "01_python_bridge.py",
    "02_pandas_timeseries.py",
    "03_signal_delay.py",
    "04_sentiment_factor.py",
    "05_walk_forward.py",
]
LABS = [f"{index:02d}_{name}_lab.py" for index, name in enumerate(
    [
        "market_basics",
        "quant_hypothesis",
        "project_pipeline",
        "python_returns",
        "pandas_alignment",
        "market_data",
        "backtest_cost",
        "sentiment",
        "walk_forward",
        "data_quality",
        "capstone",
    ],
    start=1,
)]


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


@pytest.mark.parametrize("lab", LABS)
def test_learning_lab_runs(lab: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "learning" / "labs" / lab)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert "LAB_OK" in result.stdout
