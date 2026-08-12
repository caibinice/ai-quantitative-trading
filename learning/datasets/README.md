# Teaching Dataset Notes

**English | [简体中文](./README_CN.md)**

Every CSV in this directory is a small, hand-crafted teaching sample. The data does not represent real security prices and must not be used for investment decisions. Missing dates, duplicate records, abnormal prices, and future announcements are intentionally preserved so they can be inspected, modified, and validated locally.

Each dataset maps to one runnable script under `learning/labs/`. The corresponding web lesson provides its download link, command, expected output, and self-check steps.

Conventions:

- Dates use `YYYY-MM-DD`; timestamps use ISO 8601 with an explicit `+08:00` offset.
- Returns are stored as decimals, so `0.025` means `2.5%`.
- Amounts and prices have no real-world unit, and ticker symbols are teaching identifiers only.
- Run the dataset unchanged first, then modify one parameter at a time and record the output difference.
