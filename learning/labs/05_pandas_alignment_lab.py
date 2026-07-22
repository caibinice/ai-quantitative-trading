"""跟练 05：让 pandas 按日期标签对齐，而不是按行号硬拼。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).parents[1] / "datasets" / "05_pandas_alignment.csv"


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["date"])
    wide = frame.pivot(index="date", columns="symbol", values="close").sort_index()
    calendar = pd.bdate_range(wide.index.min(), wide.index.max())
    aligned = wide.reindex(calendar)
    missing = {
        symbol: aligned.index[aligned[symbol].isna()].strftime("%Y-%m-%d").tolist()
        for symbol in aligned.columns
    }
    returns = aligned.pct_change(fill_method=None)
    print("shape=", aligned.shape)
    print("missing_dates=", missing)
    print("last_returns=", returns.iloc[-1].round(4).to_dict())
    assert missing["AAA"] == ["2026-03-05"]
    assert missing["BBB"] == ["2026-03-03"]
    print("LAB_OK")


if __name__ == "__main__":
    main()
