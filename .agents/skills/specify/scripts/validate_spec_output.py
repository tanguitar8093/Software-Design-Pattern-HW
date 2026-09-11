# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


RE_STORY_HEADING = re.compile(
    r"^### User Story (\d+) - .+ \(Priority: P(\d+)\)$",
    re.MULTILINE,
)
RE_PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
RE_FR = re.compile(r"- \*\*FR-(\d+)\*\*:")
RE_NFR = re.compile(r"- \*\*NFR-(\d+)\*\*:")
RE_SC = re.compile(r"- \*\*SC-(\d+)\*\*:")
RE_PACKAGE_NAME = re.compile(r"^\d{3}-.+$")
RE_ONE_LINE_GWT = re.compile(r"\*\*Given\*\*.+\*\*When\*\*.+\*\*Then\*\*")
RE_THEN_INLINE = re.compile(r"^\s*\*\*Then\*\*[ \t]+\S", re.MULTILINE)
RE_OLD_GWT = re.compile(r"\*\*假設\*\*.+\*\*當\*\*.+\*\*則\*\*")
RE_OLD_FR = re.compile(r"US\d+-FR\d+")
RE_OLD_SC = re.compile(r"US\d+-SC\d+")
RE_OLD_GR = re.compile(r"\*\*GR-\d+\*\*")


@dataclass
class StoryBlock:
    number: int
    start: int
    end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="檢查 specify 產出的 spec 結構是否有效。")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="要直接檢查的 spec Markdown 檔案路徑")
    group.add_argument("--package", help="要檢查的 NNN-plan-package；預設會對應到 specs/<package>/spec.md")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="workspace 根目錄；使用 --package 時會從此目錄推導 specs/<package>/spec.md",
    )
    return parser.parse_args()


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    return path.read_text(encoding="utf-8")


def resolve_input_path(args: argparse.Namespace) -> Path:
    if args.input:
        return Path(args.input)

    assert args.package is not None
    if not RE_PACKAGE_NAME.match(args.package):
        raise ValueError(
            f"Invalid package name: {args.package}. Expected format like 001-overtime-correction"
        )

    workspace_root = Path(args.workspace_root)
    return workspace_root / "specs" / args.package / "spec.md"


def build_story_blocks(text: str) -> list[StoryBlock]:
    matches = list(RE_STORY_HEADING.finditer(text))
    blocks: list[StoryBlock] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(
            StoryBlock(
                number=int(match.group(1)),
                start=start,
                end=end,
                text=text[start:end],
            )
        )
    return blocks


def ensure_contiguous(values: list[int], label: str, errors: list[str]) -> None:
    if not values:
        errors.append(f"{label} 不可為空。")
        return
    expected = list(range(1, len(values) + 1))
    if values != expected:
        errors.append(f"{label} 必須連續遞增，目前為 {values}，預期為 {expected}。")


def validate_story_structure(stories: list[StoryBlock], errors: list[str]) -> None:
    story_numbers = [story.number for story in stories]
    ensure_contiguous(story_numbers, "User Story 編號", errors)

    required_markers = [
        "**為何為此優先級**:",
        "**獨立驗證方式**:",
        "**驗收情境**:",
        "**功能需求（FR）**:",
        "**Given**",
        "**When**",
        "**Then**",
    ]

    for story in stories:
        for marker in required_markers:
            if marker not in story.text:
                errors.append(f"User Story {story.number} 缺少區塊：{marker}")

        if "作為" not in story.text or "我希望" not in story.text:
            errors.append(f"User Story {story.number} 必須使用「作為…我希望…」敘述。")

        fr_in_story = [int(num) for num in RE_FR.findall(story.text)]
        if not fr_in_story:
            errors.append(f"User Story {story.number} 至少需要一條 FR。")


def validate_ids(text: str, errors: list[str]) -> None:
    fr_numbers = [int(num) for num in RE_FR.findall(text)]
    nfr_numbers = [int(num) for num in RE_NFR.findall(text)]
    sc_numbers = [int(num) for num in RE_SC.findall(text)]
    ensure_contiguous(fr_numbers, "FR 編號", errors)
    if nfr_numbers:
        ensure_contiguous(nfr_numbers, "NFR 編號", errors)
    ensure_contiguous(sc_numbers, "SC 編號", errors)


def validate_gwt_format(text: str, errors: list[str]) -> None:
    if RE_ONE_LINE_GWT.search(text):
        errors.append("驗收情境不得把 Given／When／Then 寫成一句話。")
    if RE_THEN_INLINE.search(text):
        errors.append("`**Then**` 必須單獨成行，結果用條列，不可把結果接在同一行。")
    if RE_OLD_GWT.search(text):
        errors.append("驗收情境不得使用 `假設 / 當 / 則`。")


def validate_forbidden_legacy(text: str, errors: list[str]) -> None:
    if RE_OLD_FR.search(text):
        errors.append("不得使用 `USn-FRm` 編號。")
    if RE_OLD_SC.search(text):
        errors.append("不得使用 `USn-SCm` 編號。")
    if RE_OLD_GR.search(text):
        errors.append("不得使用 `GR-xxx`；跨故事限制改掛全域 `FR-nnn`。")
    if "**規格名稱**" in text:
        errors.append("表頭不得使用 `規格名稱`，應改為 `功能分支`。")
    if "**輸入需求**" in text:
        errors.append("表頭不得使用 `輸入需求`，應改為 `**輸入**:`。")
    if "## 規格改動" in text:
        errors.append("新建功能不得包含 `## 規格改動`。")
    if "## 使用者故事與驗證" in text:
        errors.append("章節應使用 `## 使用者情境與測試`，不得使用 `## 使用者故事與驗證`。")
    if re.search(r"^### 使用者故事 \d+", text, re.MULTILINE):
        errors.append("故事標題必須使用 `### User Story N - ... (Priority: Pn)`，不得使用 `### 使用者故事 N`。")
    if "## 共通規則與全域約束" in text:
        errors.append("跨故事限制應放在 `## 需求` 的全域需求，不得使用 `共通規則與全域約束`。")


def validate_header_and_input(text: str, errors: list[str]) -> None:
    header = text.split("## 使用者情境與測試", 1)[0]
    if "**功能分支**:" not in header and "**功能分支**：" not in header:
        errors.append("缺少 `**功能分支**:` 表頭欄位。")
    if "**輸入**:" not in header and "**輸入**：" not in header:
        errors.append("缺少 `**輸入**:` 表頭欄位。")
    if "來源" not in header:
        errors.append("`**輸入**:` 底下必須包含 `來源`。")
    if "原始需求" not in header:
        errors.append("`**輸入**:` 底下必須包含 `原始需求`。")
    if "使用者澄清決策" not in header:
        errors.append("`**輸入**:` 底下必須包含 `使用者澄清決策`。")
    input_match = re.search(r"\*\*輸入\*\*[：:]\s*(\S+)", header)
    if input_match and not input_match.group(1).startswith("\n") and "來源" not in input_match.group(0):
        # Catch `**輸入**: 一整段` on the same line.
        rest = header.split("**輸入**", 1)[1]
        first_line = rest.splitlines()[0]
        if len(first_line.strip(" ：:")) > 20:
            errors.append("`**輸入**:` 不得把需求原文擠在同一長行；應改為來源／原始需求／使用者澄清決策條列。")
    if "<br>" in header:
        errors.append("表頭不得使用 `<br>`，各欄必須分行書寫。")


def validate_common_sections(text: str, errors: list[str]) -> None:
    if not text.startswith("# 功能規格："):
        errors.append("文件必須以 `# 功能規格：...` 開頭。")
    if "## 使用者情境與測試 *(必填)*" not in text:
        errors.append("缺少 `## 使用者情境與測試 *(必填)*` 章節。")
    if "### 邊界情況" not in text:
        errors.append("缺少 `### 邊界情況` 章節。")
    if "## 需求 *(必填)*" not in text:
        errors.append("缺少 `## 需求 *(必填)*` 章節。")
    if "## 成功標準 *(必填)*" not in text:
        errors.append("缺少 `## 成功標準 *(必填)*` 章節。")
    validate_header_and_input(text, errors)
    validate_forbidden_legacy(text, errors)
    validate_gwt_format(text, errors)

    placeholders = RE_PLACEHOLDER.findall(text)
    if placeholders:
        errors.append(f"文件仍殘留 placeholder：{', '.join(sorted(set(placeholders)))}")


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
    validate_common_sections(text, errors)
    stories = build_story_blocks(text)
    if not stories:
        errors.append("至少需要一個 `### User Story N - ... (Priority: Pn)` 區塊。")
    else:
        validate_story_structure(stories, errors)
    validate_ids(text, errors)

    if errors:
        print("SPEC VALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("SPEC VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
