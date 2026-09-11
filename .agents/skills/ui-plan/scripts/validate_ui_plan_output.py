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
USER_STORY_HEADING_RE = re.compile(r"^### User Story (\d+)：.+$")
PAGE_HEADING_RE = re.compile(r"^### 頁面：.+$")
TITLE_RE = re.compile(r"^# UI 計畫：.+$")
BRANCH_RE = re.compile(r"^\*\*功能分支\*\*:\s*`[^`]+`$")
CREATED_DATE_RE = re.compile(r"^\*\*建立日期\*\*:\s*\d{4}-\d{2}-\d{2}$")
STATUS_RE = re.compile(r"^\*\*狀態\*\*:\s*.+$")
MERMAID_FENCE_RE = re.compile(r"^```mermaid\s*$")
PROTOTYPE_FILE_RE = re.compile(r"對應雛形檔案：\s*`([^`]+)`")

REQUIRED_TOP_LEVEL = [
    "## 視覺方向",
    "## 操作流程",
    "## 頁面設計",
    "## 雛形輸出規劃",
    "## 假設",
]

VISUAL_MARKERS = [
    "風格來源",
    "本次風格結論",
    "視覺重點",
    "審美原則",
]

PAGE_REQUIRED_MARKERS = [
    "#### 職責",
    "#### 頁面編排",
    "#### 呈現內容",
    "#### 操作 Flow",
    "#### 狀態",
    "#### 導覽",
    "#### API 對應",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the structure of a ui-plan Markdown artifact and sibling prototypes."
    )
    parser.add_argument("--input", required=True, help="Path to the ui-plan.md file")
    return parser.parse_args()


def find_section_ranges(
    lines: list[str], heading_re: re.Pattern[str], stop_headers: set[str]
) -> list[tuple[int, int]]:
    headings = [idx for idx, line in enumerate(lines) if heading_re.match(line.strip())]
    if not headings:
        return []

    stop_index = next(
        (idx for idx, line in enumerate(lines) if line.strip() in stop_headers),
        len(lines),
    )

    ranges: list[tuple[int, int]] = []
    for position, start in enumerate(headings):
        if position + 1 < len(headings):
            end = headings[position + 1]
        else:
            end = stop_index
        ranges.append((start, end))
    return ranges


def section_has_marker(section_lines: list[str], marker: str) -> bool:
    return any(line.strip() == marker for line in section_lines)


def section_has_mermaid(section_lines: list[str]) -> bool:
    return any(MERMAID_FENCE_RE.match(line.strip()) for line in section_lines)


def validate_assumption_section(lines: list[str]) -> list[str]:
    errors: list[str] = []
    start = next((idx for idx, line in enumerate(lines) if line.strip() == "## 假設"), None)
    if start is None:
        return errors

    if start != max(idx for idx, line in enumerate(lines) if line.startswith("## ")):
        errors.append("## 假設 must be the last top-level section")

    bullet_count = 0
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            bullet_count += 1

    if bullet_count < 1:
        errors.append("## 假設 must contain at least one `- ` bullet item")
    return errors


def validate_user_story(section_lines: list[str], label: str) -> list[str]:
    errors: list[str] = []
    text = "\n".join(section_lines)

    if not section_has_mermaid(section_lines):
        errors.append(f"{label}: missing mermaid sequence fence")

    if "對應：" not in text and "對應:" not in text:
        errors.append(f"{label}: missing `對應：` traceability block")

    has_us = bool(re.search(r"\*\*US-\d+\*\*|US-\d+", text))
    has_fr = bool(re.search(r"\*\*FR-\d+\*\*|FR-\d+|US\d+-FR\d+", text))
    has_ac = bool(re.search(r"\*\*AC-\d+-\d+\*\*|AC-\d+-\d+", text))
    if not has_us:
        errors.append(f"{label}: missing US traceability")
    if not has_fr:
        errors.append(f"{label}: missing FR traceability")
    if not has_ac:
        errors.append(f"{label}: missing AC traceability")

    return errors


def validate_page(section_lines: list[str], label: str) -> list[str]:
    errors: list[str] = []
    text = "\n".join(section_lines)

    if "對應雛形檔案" not in text:
        errors.append(f"{label}: missing 對應雛形檔案")
    if "進入條件" not in text:
        errors.append(f"{label}: missing 進入條件")

    for marker in PAGE_REQUIRED_MARKERS:
        if not section_has_marker(section_lines, marker):
            errors.append(f"{label}: missing `{marker}`")

    if not section_has_mermaid(section_lines):
        errors.append(f"{label}: missing mermaid fence")

    if "| 狀態 ID" not in text or "觸發時間" not in text or "畫面文案" not in text:
        errors.append(f"{label}: 狀態 table must include 狀態 ID, 觸發時間 and 畫面文案")

    if "| 操作" not in text or "前往頁面" not in text:
        errors.append(f"{label}: 導覽 table must include 操作 and 前往頁面")

    if "| 使用者操作" not in text or "| API" not in text:
        errors.append(f"{label}: API 對應 table must include 使用者操作 and API")

    return errors


def validate_user_story_numbering(lines: list[str]) -> list[str]:
    errors: list[str] = []
    numbers: list[int] = []
    for line in lines:
        match = USER_STORY_HEADING_RE.match(line.strip())
        if match:
            numbers.append(int(match.group(1)))

    if not numbers:
        errors.append("missing at least one `### User Story N：` section")
        return errors

    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errors.append(
            "User Story numbering must be contiguous from 1; "
            f"found {numbers}"
        )
    return errors


def validate_visual_direction(lines: list[str]) -> list[str]:
    errors: list[str] = []
    start = next((idx for idx, line in enumerate(lines) if line.strip() == "## 視覺方向"), None)
    if start is None:
        return errors
    end = next(
        (idx for idx, line in enumerate(lines[start + 1 :], start=start + 1) if line.startswith("## ")),
        len(lines),
    )
    text = "\n".join(lines[start:end])
    for marker in VISUAL_MARKERS:
        if marker not in text:
            errors.append(f"## 視覺方向: missing `{marker}`")
    return errors


def validate_prototypes(path: Path, content: str) -> list[str]:
    errors: list[str] = []
    base = path.parent
    files = PROTOTYPE_FILE_RE.findall(content)
    if not files:
        errors.append("missing at least one 對應雛形檔案")
        return errors

    if "ui/index.html" not in files:
        errors.append("multi-page prototypes must include `ui/index.html` as product entry")

    for relative in files:
        target = base / relative
        if not target.exists():
            errors.append(f"prototype file not found: {relative}")
    return errors


def validate(path: Path) -> list[str]:
    if not path.exists():
        return [f"Input not found: {path}"]

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    errors: list[str] = []

    head = [line.strip() for line in lines[:10]]
    if not lines or not TITLE_RE.match(head[0] if head else ""):
        errors.append("missing top-level heading '# UI 計畫：…'")
    if not any(BRANCH_RE.match(line) for line in head):
        errors.append("missing metadata line for 功能分支")
    if not any(CREATED_DATE_RE.match(line) for line in head):
        errors.append("missing metadata line for 建立日期")
    if not any(STATUS_RE.match(line) for line in head):
        errors.append("missing metadata line for 狀態")

    for header in REQUIRED_TOP_LEVEL:
        if not any(line.strip() == header for line in lines):
            errors.append(f"missing `{header}`")

    if any(line.strip().startswith("## 業務邏輯") for line in lines):
        errors.append("must not use `## 業務邏輯`; use `## 操作流程` / `### User Story N：`")
    if re.search(r"^### 使用者故事 \d+", content, re.MULTILINE):
        errors.append("故事標題必須使用 `### User Story N：`，不得使用 `### 使用者故事 N`。")
    if any(line.strip() == "## 頁面總覽（導覽關係）" for line in lines):
        errors.append("頁面總覽 must be `### 頁面總覽（導覽關係）` under `## 頁面設計`")

    if PLACEHOLDER_RE.search(content):
        errors.append("output still contains unreplaced {{PLACEHOLDER}} tokens")

    errors.extend(validate_assumption_section(lines))
    errors.extend(validate_visual_direction(lines))
    errors.extend(validate_user_story_numbering(lines))

    story_stop = {"## 頁面設計", "## 雛形輸出規劃", "## 假設"}
    story_ranges = find_section_ranges(lines, USER_STORY_HEADING_RE, story_stop)
    for start, end in story_ranges:
        label = lines[start].strip()
        errors.extend(validate_user_story(lines[start:end], label))

    page_stop = {"### 頁面總覽（導覽關係）", "## 雛形輸出規劃", "## 假設"}
    page_ranges = find_section_ranges(lines, PAGE_HEADING_RE, page_stop)
    if not page_ranges:
        errors.append("missing at least one `### 頁面：` section")
    else:
        for start, end in page_ranges:
            label = lines[start].strip()
            errors.extend(validate_page(lines[start:end], label))

    overview_idx = next(
        (idx for idx, line in enumerate(lines) if line.strip() == "### 頁面總覽（導覽關係）"),
        None,
    )
    if overview_idx is None:
        errors.append("missing `### 頁面總覽（導覽關係）`")
    else:
        overview_end = next(
            (
                idx
                for idx, line in enumerate(lines[overview_idx + 1 :], start=overview_idx + 1)
                if line.startswith("## ") or line.startswith("### 頁面：")
            ),
            len(lines),
        )
        overview = "\n".join(lines[overview_idx:overview_end])
        if "```mermaid" not in overview:
            errors.append("頁面總覽: missing mermaid flowchart fence")
        if "| 頁面" not in overview or "主要 US" not in overview:
            errors.append("頁面總覽: table must include 頁面 and 主要 US")

    errors.extend(validate_prototypes(path, content))
    return errors


def main() -> int:
    args = parse_args()
    path = Path(args.input)
    errors = validate(path)

    if errors:
        print(f"INVALID: {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
