# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
RE_PACKAGE_NAME = re.compile(r"^\d{3}-.+$")
RE_STORY = re.compile(r"^## User Story (\d+) - .+$", re.MULTILINE)
RE_CASE_HEADING = re.compile(
    r"^### ((?:FE|BE)-JOURNEY-\d+|(?:BE-API|FE-E2E)-\d+[A-Z]?|GLOBAL-NFR-\d+) - .+$",
    re.MULTILINE,
)
RE_BE_REPO_CASE = re.compile(r"^### BE-REPO-", re.MULTILINE)
RE_LAYER_HEADING = re.compile(r"^## (後端|前端|整合)\s*$", re.MULTILINE)
RE_GHERKIN = re.compile(r"^```gherkin\s*$", re.MULTILINE)
RE_OLD_SCENARIO = re.compile(r"^#### Scenario:", re.MULTILINE)

REQUIRED_SECTIONS = [
    "## 上游輸入與規劃邊界",
    "## 本輪不納入測試的項目",
    "## 案例分類與 TDD 關係",
    "## 共用前置資料（Arrange Fixtures）",
    "## 全域 NFR 測試規劃",
    "## 建議 TDD 實作順序",
]

REQUIRED_SLICE_FIELDS = [
    "**案例類型**: TDD 切片（Slice）",
    "**對應需求**:",
    "**唯一測試意圖**:",
    "**受測部位**:",
    "**前置資料（Arrange Fixture）**:",
    "**操作（Act）輸入**:",
    "**觀測通道／預期輸出**:",
    "**必須維持不變**:",
    "**預期 RED 原因**:",
    "**本案例不驗證**:",
]

REQUIRED_JOURNEY_FIELDS = [
    "**案例類型**: 驗收旅程（Acceptance Journey）",
    "**組成切片（Slice）**:",
    "**前置資料（Arrange Fixture）**:",
    "**操作（Act）輸入**:",
    "**觀測通道／預期輸出**:",
    "**本案例不驗證**:",
]

LIST_FIELDS = [
    "**受測部位**:",
    "**操作（Act）輸入**:",
    "**觀測通道／預期輸出**:",
    "**組成切片（Slice）**:",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="檢查 testplan 產出的結構是否有效。")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="要直接檢查的 testplan Markdown 檔案路徑")
    group.add_argument(
        "--package",
        help="要檢查的 NNN-plan-package；預設對應 specs/<package>/testplan.md",
    )
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="workspace 根目錄；使用 --package 時會從此目錄推導 specs/<package>/testplan.md",
    )
    return parser.parse_args()


def resolve_input_path(args: argparse.Namespace) -> Path:
    if args.input:
        return Path(args.input)

    assert args.package is not None
    if not RE_PACKAGE_NAME.match(args.package):
        raise ValueError(
            f"Invalid package name: {args.package}. Expected format like 001-overtime-correction"
        )
    return Path(args.workspace_root) / "specs" / args.package / "testplan.md"


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    return path.read_text(encoding="utf-8")


def case_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(RE_CASE_HEADING.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[start:end]))
    return blocks


def field_has_same_line_value(block: str, field: str) -> bool:
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith(field):
            remainder = stripped[len(field) :].strip()
            return bool(remainder)
    return False


def validate_document(text: str, errors: list[str]) -> None:
    if not text.startswith("# 測試計劃："):
        errors.append("文件必須以 `# 測試計劃：...` 開頭。")
    if "**功能分支**:" not in text and "**功能分支**：" not in text:
        errors.append("缺少 `**功能分支**:` 表頭欄位。")
    if "**建立日期**:" not in text and "**建立日期**：" not in text:
        errors.append("缺少 `**建立日期**:` 表頭欄位。")
    if "**狀態**:" not in text and "**狀態**：" not in text:
        errors.append("缺少 `**狀態**:` 表頭欄位。")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"缺少章節：{section}")

    if not RE_STORY.search(text):
        errors.append("至少需要一個 `## User Story N - ...` 區塊。")

    for match in RE_LAYER_HEADING.finditer(text):
        errors.append(f"不得使用第一層章節 `## {match.group(1)}`。")
    if RE_GHERKIN.search(text):
        errors.append("不得使用 Gherkin fence；案例改寫成旅程／切片欄位。")
    if RE_OLD_SCENARIO.search(text):
        errors.append("不得使用 `#### Scenario:`；改用 `### FE-JOURNEY-*`／`### BE-API-*`／`### FE-E2E-*`。")
    if RE_BE_REPO_CASE.search(text):
        errors.append("不得使用 `BE-REPO-*` persistence seam 作為案例。")
    if "**案例類型**: Acceptance Journey" in text:
        errors.append("案例類型應寫 `驗收旅程（Acceptance Journey）`，不可只寫英文。")
    if "**案例類型**: TDD Slice" in text:
        errors.append("案例類型應寫 `TDD 切片（Slice）`，不可只寫英文。")
    if "**Arrange Fixture**:" in text:
        errors.append("欄位應寫 `前置資料（Arrange Fixture）`，不可只寫 `Arrange Fixture`。")
    if "**Act 輸入**:" in text or "**動作（Act）輸入**:" in text:
        errors.append("欄位應寫 `操作（Act）輸入`。")
    if re.search(r"^\s*- \*\*觀測通道\*\*:", text, re.MULTILINE) and "**觀測通道／預期輸出**:" not in text:
        errors.append("`觀測通道` 必須與預期輸出合為 `觀測通道／預期輸出`。")
    if re.search(r"^\s*- \*\*預期輸出\*\*:", text, re.MULTILINE):
        errors.append("不得另開 `預期輸出` 欄；應併入 `觀測通道／預期輸出`。")

    placeholders = RE_PLACEHOLDER.findall(text)
    if placeholders:
        errors.append(f"文件仍殘留 placeholder：{', '.join(sorted(set(placeholders)))}")


def validate_cases(text: str, errors: list[str]) -> None:
    blocks = case_blocks(text)
    if not blocks:
        errors.append("至少需要一個旅程或切片案例。")
        return

    seen: dict[str, int] = {}
    journey_count = 0
    slice_count = 0
    for case_id, block in blocks:
        seen[case_id] = seen.get(case_id, 0) + 1
        is_journey = "JOURNEY" in case_id
        if is_journey:
            journey_count += 1
            for field in REQUIRED_JOURNEY_FIELDS:
                if field not in block:
                    errors.append(f"{case_id} 缺少欄位：{field}")
            if "- `" not in block.split("**組成切片（Slice）**:", 1)[-1].split("**對應需求**:", 1)[0]:
                errors.append(f"{case_id} 的 `組成切片（Slice）` 必須條列依賴的切片 ID。")
        else:
            slice_count += 1
            for field in REQUIRED_SLICE_FIELDS:
                if field not in block:
                    errors.append(f"{case_id} 缺少欄位：{field}")

        for field in LIST_FIELDS:
            if field in block and field_has_same_line_value(block, field):
                errors.append(f"{case_id} 的 `{field.rstrip(':')}` 不得把多值擠在同一行，應改換行條列。")

        observe_block = block.split("**觀測通道／預期輸出**:", 1)
        if len(observe_block) == 2:
            observe_text = observe_block[1].split("**必須維持不變**:", 1)[0]
            if "→" not in observe_text:
                errors.append(f"{case_id} 的 `觀測通道／預期輸出` 應寫成 `在哪裡看 → 應看到什麼`。")

    duplicates = [case_id for case_id, count in seen.items() if count > 1]
    if duplicates:
        errors.append(f"案例 ID 重複：{', '.join(sorted(duplicates))}")
    if journey_count < 1:
        errors.append("至少需要一則驗收旅程（`FE-JOURNEY-*` 或 `BE-JOURNEY-*`）。")
    if slice_count < 1:
        errors.append("至少需要一則 TDD 切片（`BE-API-*` 或 `FE-E2E-*`）。")


def main() -> int:
    args = parse_args()
    try:
        input_path = resolve_input_path(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        text = load_text(input_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    errors: list[str] = []
    validate_document(text, errors)
    validate_cases(text, errors)

    if errors:
        print("TESTPLAN VALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("TESTPLAN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
