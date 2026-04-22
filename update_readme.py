from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _format_average(value: Any) -> str:
    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    return str(value)


def _build_underfilled_table(underfilled: list[dict[str, Any]]) -> str:
    lines = ["| DDC | Sample Number |", "| --- | --- |"]
    if underfilled:
        for item in underfilled:
            ddc = str(item.get("ddc", "")).zfill(3)
            sample_number = item.get("sample_number", 0)
            lines.append(f"| {ddc} | {sample_number} |")
    else:
        lines.append("| None | 0 |")
    return "\n".join(lines)


def build_statistics_block(stats: dict[str, Any]) -> str:
    valid_sample_total = stats.get("valid_sample_total", 0)
    min_description_length = stats.get("min_description_length", 20)
    max_description_length = stats.get("max_description_length", 1000)
    average_description_length = _format_average(stats.get("average_description_length", 0))
    underfilled_ddc = stats.get("underfilled_ddc", [])

    table = _build_underfilled_table(underfilled_ddc)

    return (
        "## Statistics\n\n"
        "### DDC data distribution\n\n"
        "DDC that already having 100 samples will not show details of the distribution.\n\n"
        f"**Vaild samples number in total: {valid_sample_total}**\n\n"
        "**DDC number that not satisfy the requirement of 100 samples:**\n"
        f"{table}\n\n"
        "### DDC data quality\n\n"
        f"**Minimal length of description: {min_description_length}**\n"
        f"**Maximal length of description: {max_description_length}**\n"
        f"**Average length of description: {average_description_length}**\n"
    )


def replace_statistics_section(readme_content: str, statistics_block: str) -> str:
    pattern = re.compile(r"(?ms)^## Statistics\s*\n.*?(?=^##\s|\Z)")

    if pattern.search(readme_content):
        return pattern.sub(statistics_block + "\n", readme_content, count=1)

    base = readme_content.rstrip() + "\n\n"
    return base + statistics_block + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Update README statistics section.")
    parser.add_argument("--stats-file", default="statistics.json", help="JSON statistics file.")
    parser.add_argument("--readme", default="README.md", help="README file to update.")
    args = parser.parse_args()

    stats_file = Path(args.stats_file)
    readme_file = Path(args.readme)

    stats = json.loads(stats_file.read_text(encoding="utf-8"))
    readme_content = readme_file.read_text(encoding="utf-8")

    new_statistics_block = build_statistics_block(stats)
    new_readme_content = replace_statistics_section(readme_content, new_statistics_block)

    if new_readme_content != readme_content:
        readme_file.write_text(new_readme_content, encoding="utf-8")
        print(f"Updated {readme_file}")
    else:
        print("README is already up to date.")


if __name__ == "__main__":
    main()