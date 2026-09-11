# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
TITLE_RE = re.compile(r"^# 系統分析：.+$")
BRANCH_RE = re.compile(r"^\*\*功能分支\*\*:\s*`[^`]+`$")
CREATED_DATE_RE = re.compile(r"^\*\*建立日期\*\*:\s*\d{4}-\d{2}-\d{2}$")
STATUS_RE = re.compile(r"^\*\*狀態\*\*:\s*.+$")
FLOW_VERSION_RE = re.compile(r"^流程版本:\s*2$")

REQUIRED_TOP_LEVEL = (
    "## 摘要",
    "## 技術背景",
    "## 專案結構",
)

SUMMARY_SUBHEADINGS = (
    "### 規格功能概述",
    "### 技術選型概述",
)

TECH_BACKGROUND_SUBHEADINGS = (
    "### 使用語言／版本",
    "### 主要依賴",
    "### 資料儲存",
    "### 測試環境",
    "### 開發平台",
    "### 專案類型",
    "### 效能目標",
    "### 技術約束",
    "### 實作規模／範圍",
)

STRUCTURE_SUBHEADINGS = (
    "### 文件（本功能）",
    "### 原始碼（儲存庫根目錄）",
    "### 結構決策",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the structure of a plan.md Markdown artifact."
    )
    parser.add_argument("--input", required=True, help="Path to the plan.md file")
    return parser.parse_args()


def heading_indices(lines: list[str], heading: str) -> list[int]:
    return [idx for idx, line in enumerate(lines) if line.strip() == heading]


def first_heading_index(lines: list[str], heading: str) -> int | None:
    indices = heading_indices(lines, heading)
    return indices[0] if indices else None


def section_slice(lines: list[str], start: int, stop_headings: set[str]) -> list[str]:
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped in stop_headings or (
            stripped.startswith("## ") and stripped not in stop_headings
        ):
            # stop at next same-level or known boundary
            if stripped.startswith("## "):
                end = idx
                break
    return lines[start:end]


def has_bullet(section_lines: list[str]) -> bool:
    return any(line.strip().startswith("- ") for line in section_lines)


def validate_metadata(lines: list[str]) -> list[str]:
    errors: list[str] = []
    if not lines or not TITLE_RE.match(lines[0].strip()):
        errors.append("H1 must match `# 系統分析：...`")

    head = [line.strip() for line in lines[:12]]
    if not any(BRANCH_RE.match(line) for line in head):
        errors.append("missing `**功能分支**: \\`...\\`` metadata line")
    if not any(CREATED_DATE_RE.match(line) for line in head):
        errors.append("missing `**建立日期**: YYYY-MM-DD` metadata line")
    if not any(STATUS_RE.match(line) for line in head):
        errors.append("missing `**狀態**: ...` metadata line")
    return errors


def validate_top_level(lines: list[str]) -> list[str]:
    errors: list[str] = []
    positions: list[int] = []
    for heading in REQUIRED_TOP_LEVEL:
        idx = first_heading_index(lines, heading)
        if idx is None:
            errors.append(f"missing `{heading}`")
        else:
            positions.append(idx)

    if len(positions) == len(REQUIRED_TOP_LEVEL):
        if positions != sorted(positions):
            errors.append(
                "top-level sections must appear in order: 摘要 → 技術背景 → 專案結構"
            )
    return errors


def validate_summary(lines: list[str]) -> list[str]:
    errors: list[str] = []
    start = first_heading_index(lines, "## 摘要")
    if start is None:
        return errors

    stop = {"## 技術背景", "## 專案結構"}
    section = section_slice(lines, start, stop)
    positions: list[int] = []
    for heading in SUMMARY_SUBHEADINGS:
        idx = next(
            (i for i, line in enumerate(section) if line.strip() == heading), None
        )
        if idx is None:
            errors.append(f"missing `{heading}` under ## 摘要")
        else:
            positions.append(idx)
            # ensure non-empty prose after heading
            body: list[str] = []
            for line in section[idx + 1 :]:
                stripped = line.strip()
                if stripped.startswith("### ") or stripped.startswith("## "):
                    break
                if stripped:
                    body.append(stripped)
            if not body:
                errors.append(f"{heading}: must contain non-empty content")

    if len(positions) == len(SUMMARY_SUBHEADINGS) and positions != sorted(positions):
        errors.append("摘要 subheadings must be 規格功能概述 → 技術選型概述")
    return errors


def validate_tech_background(lines: list[str]) -> list[str]:
    errors: list[str] = []
    start = first_heading_index(lines, "## 技術背景")
    if start is None:
        return errors

    section = section_slice(lines, start, {"## 專案結構"})
    positions: list[int] = []
    for heading in TECH_BACKGROUND_SUBHEADINGS:
        idx = next(
            (i for i, line in enumerate(section) if line.strip() == heading), None
        )
        if idx is None:
            errors.append(f"missing `{heading}` under ## 技術背景")
            continue
        positions.append(idx)
        body: list[str] = []
        for line in section[idx + 1 :]:
            stripped = line.strip()
            if stripped.startswith("### ") or stripped.startswith("## "):
                break
            body.append(line)
        if not has_bullet(body):
            errors.append(f"{heading}: must contain at least one `- ` bullet")

    if len(positions) == len(TECH_BACKGROUND_SUBHEADINGS):
        expected_order = list(range(len(positions)))
        order_by_appearance = sorted(range(len(positions)), key=lambda i: positions[i])
        if order_by_appearance != expected_order:
            errors.append("技術背景九個小標必須維持固定順序")
    return errors


def validate_project_structure(lines: list[str]) -> list[str]:
    errors: list[str] = []
    start = first_heading_index(lines, "## 專案結構")
    if start is None:
        return errors

    section = lines[start:]
    positions: list[int] = []
    for heading in STRUCTURE_SUBHEADINGS:
        idx = next(
            (i for i, line in enumerate(section) if line.strip() == heading), None
        )
        if idx is None:
            errors.append(f"missing `{heading}` under ## 專案結構")
            continue
        positions.append(idx)

    if len(positions) == len(STRUCTURE_SUBHEADINGS):
        if positions != sorted(positions):
            errors.append(
                "專案結構 order must be 文件 → 原始碼 → 結構決策 (結構決策 at bottom)"
            )

    # code fences for first two subsections
    for heading in STRUCTURE_SUBHEADINGS[:2]:
        idx = next(
            (i for i, line in enumerate(section) if line.strip() == heading), None
        )
        if idx is None:
            continue
        body: list[str] = []
        for line in section[idx + 1 :]:
            stripped = line.strip()
            if stripped.startswith("### ") or stripped.startswith("## "):
                break
            body.append(line)
        if not any(line.strip().startswith("```") for line in body):
            errors.append(f"{heading}: must include a fenced code tree")

    decision_idx = next(
        (i for i, line in enumerate(section) if line.strip() == "### 結構決策"), None
    )
    if decision_idx is not None:
        body: list[str] = []
        for line in section[decision_idx + 1 :]:
            stripped = line.strip()
            if stripped.startswith("### ") or stripped.startswith("## "):
                break
            body.append(line)
        if not has_bullet(body):
            errors.append("### 結構決策: must contain at least one `- ` bullet")

    return errors


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    if PLACEHOLDER_RE.search(text):
        errors.append("output still contains unreplaced {{PLACEHOLDER}} tokens")

    errors.extend(validate_metadata(lines))
    errors.extend(validate_top_level(lines))
    errors.extend(validate_summary(lines))
    errors.extend(validate_tech_background(lines))
    errors.extend(validate_project_structure(lines))
    if any(FLOW_VERSION_RE.match(line.strip()) for line in lines[:12]):
        frontend_marker = "前端瀏覽器端對端："
        frontend_not_applicable = re.search(
            r"前端瀏覽器端對端[：:].{0,80}不適用", text
        )
        if frontend_marker not in text:
            errors.append("流程版本 2: ### 測試環境必須記錄前端瀏覽器端對端套件或明列不適用")
        elif not frontend_not_applicable and (
            "真後端" not in text and "實際後端" not in text
        ):
            errors.append("流程版本 2: plan 必須交代前端瀏覽器測試打真後端")
    return errors


def main() -> int:
    args = parse_args()
    path = Path(args.input)
    if not path.exists():
        print(f"Input not found: {path}", file=sys.stderr)
        return 2

    errors = validate(path)
    if errors:
        print(f"FAIL: {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
