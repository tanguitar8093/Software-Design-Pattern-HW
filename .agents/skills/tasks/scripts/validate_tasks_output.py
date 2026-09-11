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
RE_STORY = re.compile(r"^## Phase \d+: User Story (\d+) - .+$", re.MULTILINE)
RE_LAYER_HEADING = re.compile(r"^## (後端|前端|整合)\s*$", re.MULTILINE)
RE_TESTPLAN_CASE = re.compile(
    r"^### ((?:FE|BE)-JOURNEY-\d+|(?:BE-API|FE-E2E)-\d+[A-Z]?|GLOBAL-NFR-\d+) - .+$",
    re.MULTILINE,
)
RE_SLICE_HEADING = re.compile(
    r"^### (?P<kind>後端切片（Slice）|前端切片（Slice）) (?P<case_id>(?:BE-API|FE-E2E)-\d+[A-Z]?) - .+$",
    re.MULTILINE,
)
RE_JOURNEY_HEADING = re.compile(
    r"^### 驗收旅程（Acceptance Journey） (?P<case_id>(?:FE|BE)-JOURNEY-\d+) - .+$",
    re.MULTILINE,
)
RE_SLICE_TASK = re.compile(
    r"\[US(\d+)\] \[SLICE ((?:BE-API|FE-E2E)-\d+[A-Z]?)\] "
    r"\[(TDD-RED|TDD-GREEN|TDD-REFACTOR|TDD-ALIGN)\]"
)
RE_REMOVE_TASK = re.compile(r"\[US(\d+)\] \[TDD-REMOVE\]")
RE_REGRESSION_TASK = re.compile(r"\[US(\d+)\] \[REGRESSION\]")
RE_JOURNEY_TASK = re.compile(
    r"\[US(\d+)\] \[JOURNEY ((?:FE|BE)-JOURNEY-\d+)\] \[ACCEPTANCE-GATE\]"
)
RE_TASK_START = re.compile(r"^- \[[ xX]\] T\d+", re.MULTILINE)
RE_CASE_ID = re.compile(r"(?:BE-API|FE-E2E)-\d+[A-Z]?")
RE_BACKEND_ID = re.compile(r"BE-API-\d+[A-Z]?")
RE_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE,
)
NOTE_HEADING = "## 備註：既有測試影響（給人看，implement 不依此執行）"

DESIGN_INPUT_FILES = [
    "spec.md",
    "plan.md",
    "testplan.md",
    "system-analyze/technical-research.md",
    "system-analyze/data-plan.md",
    "system-analyze/DDL.md",
    "system-analyze/api-plan.md",
    "system-analyze/ui-plan.md",
]

REQUIRED_SECTIONS = [
    "## 任務契約（Task Binding Contract）",
    "## Phase 1: 環境建立（Setup）",
    "## Phase 2: 基礎前置（Foundational）",
    "## 依賴關係（Dependencies）",
]

LIST_FIELDS = [
    "必讀（Must Read）:",
    "選讀（Optional）:",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="檢查 tasks 產出的結構是否有效。")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="要直接檢查的 tasks Markdown 檔案路徑")
    group.add_argument(
        "--package",
        help="要檢查的 NNN-plan-package；預設對應 specs/<package>/tasks.md",
    )
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="workspace 根目錄；使用 --package 時會從此目錄推導 specs/<package>/tasks.md",
    )
    return parser.parse_args()


def resolve_paths(
    args: argparse.Namespace,
) -> tuple[Path, Path | None, Path, Path, Path]:
    workspace_root = Path(args.workspace_root)
    if args.input:
        tasks_path = Path(args.input)
        package_dir = tasks_path.parent
        testplan_path = tasks_path.with_name("testplan.md")
        api_plan_path = package_dir / "system-analyze" / "api-plan.md"
        return (
            tasks_path,
            testplan_path if testplan_path.exists() else None,
            api_plan_path,
            package_dir,
            workspace_root,
        )

    assert args.package is not None
    if not RE_PACKAGE_NAME.match(args.package):
        raise ValueError(
            f"Invalid package name: {args.package}. Expected format like 001-overtime-correction"
        )
    package_dir = workspace_root / "specs" / args.package
    return (
        package_dir / "tasks.md",
        package_dir / "testplan.md",
        package_dir / "system-analyze" / "api-plan.md",
        package_dir,
        workspace_root,
    )


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    return path.read_text(encoding="utf-8")


def field_has_same_line_value(block: str, field: str) -> bool:
    for line in block.splitlines():
        stripped = line.strip()
        if field in stripped:
            remainder = stripped.split(field, 1)[1].strip()
            return bool(remainder)
    return False


def task_blocks(text: str) -> list[str]:
    matches = list(RE_TASK_START.finditer(text))
    blocks: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks


def validate_document(text: str, errors: list[str]) -> None:
    if not text.startswith("# 任務清單："):
        errors.append("文件必須以 `# 任務清單：...` 開頭。")
    if "**功能分支**:" not in text and "**功能分支**：" not in text:
        errors.append("缺少 `**功能分支**:` 表頭欄位。")
    if "**規格目錄**:" not in text and "**規格目錄**：" not in text:
        errors.append("缺少 `**規格目錄**:` 表頭欄位。")
    if "**輸入文件**:" not in text and "**輸入文件**：" not in text:
        errors.append("缺少 `**輸入文件**:` 表頭欄位。")
    if "**Feature Directory**:" in text:
        errors.append("表頭應寫 `規格目錄`，不可使用 `Feature Directory`。")
    if "**Input Documents**:" in text:
        errors.append("表頭應寫 `輸入文件`，不可使用 `Input Documents`。")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"缺少章節：{section}")

    if not RE_STORY.search(text):
        errors.append("至少需要一個 `## Phase N: User Story N - ...` 區塊。")

    for match in RE_LAYER_HEADING.finditer(text):
        errors.append(f"不得使用第一層章節 `## {match.group(1)}`。")
    if re.search(r"^### .*BE-REPO-", text, re.MULTILINE) or "[SLICE BE-REPO-" in text:
        errors.append("不得使用 `BE-REPO-*` persistence seam 作為任務。")
    if "task-plan/task-backend.md" in text or "task-plan/task-frontend.md" in text:
        errors.append("不得再產出或指向 `task-plan/task-*.md` 三檔。")
    if re.search(r"^### 切片（Slice） ", text, re.MULTILINE):
        errors.append("切片標題必須標明 `後端切片（Slice）` 或 `前端切片（Slice）`。")

    placeholders = RE_PLACEHOLDER.findall(text)
    if placeholders:
        errors.append(f"文件仍殘留 placeholder：{', '.join(sorted(set(placeholders)))}")


def validate_headings(text: str, errors: list[str]) -> dict[str, str]:
    heading_kinds: dict[str, str] = {}
    for match in RE_SLICE_HEADING.finditer(text):
        case_id = match.group("case_id")
        kind = match.group("kind")
        heading_kinds[case_id] = kind
        if case_id.startswith("BE-") and kind != "後端切片（Slice）":
            errors.append(f"{case_id} 應使用 `後端切片（Slice）` 標題。")
        if case_id.startswith("FE-") and kind != "前端切片（Slice）":
            errors.append(f"{case_id} 應使用 `前端切片（Slice）` 標題。")
    for match in RE_JOURNEY_HEADING.finditer(text):
        heading_kinds[match.group("case_id")] = "驗收旅程（Acceptance Journey）"
    return heading_kinds


def validate_task_fields(text: str, errors: list[str]) -> None:
    blocks = task_blocks(text)
    if not blocks:
        errors.append("至少需要一個核取方塊任務。")
        return

    for block in blocks:
        first_line = block.splitlines()[0]
        if "必讀（Must Read）:" not in block:
            errors.append(f"任務缺少必讀（Must Read）：{first_line[:80]}")
        if "原因（Why）:" not in block:
            errors.append(f"任務缺少原因（Why）：{first_line[:80]}")
        for field in LIST_FIELDS:
            if field in block and field_has_same_line_value(block, field):
                errors.append(
                    f"任務的 `{field.rstrip(':')}` 不得把多值擠在同一行：{first_line[:80]}"
                )
        if "[TDD-ALIGN]" in first_line:
            if "testplan.md" not in block:
                errors.append(f"ALIGN 必讀必須包含 testplan 目標案例：{first_line[:80]}")
            if "tests/" not in block:
                errors.append(f"ALIGN 必讀必須包含現行測檔路徑：{first_line[:80]}")
        if "[TDD-REMOVE]" in first_line:
            if "tests/" not in block:
                errors.append(f"REMOVE 必讀必須包含現行測檔路徑：{first_line[:80]}")
            if "[SLICE " in first_line:
                errors.append(f"REMOVE 不得使用 `[SLICE …]` 標題：{first_line[:80]}")


def collect_slice_steps(text: str) -> dict[str, dict[str, int]]:
    steps: dict[str, dict[str, int]] = {}
    for match in RE_SLICE_TASK.finditer(text):
        case_id = match.group(2)
        step = match.group(3)
        steps.setdefault(case_id, {})[step] = match.start()
    return steps


def collect_journey_gates(text: str) -> dict[str, int]:
    gates: dict[str, int] = {}
    for match in RE_JOURNEY_TASK.finditer(text):
        gates[match.group(2)] = match.start()
    return gates


def first_slice_step(found: dict[str, int]) -> tuple[str, int] | None:
    if "TDD-ALIGN" in found:
        return "TDD-ALIGN", found["TDD-ALIGN"]
    if "TDD-RED" in found:
        return "TDD-RED", found["TDD-RED"]
    return None


def validate_slice_chains_and_order(text: str, errors: list[str]) -> None:
    steps = collect_slice_steps(text)
    for case_id, found in steps.items():
        has_align = "TDD-ALIGN" in found
        has_red = "TDD-RED" in found
        if has_align and has_red:
            errors.append(f"{case_id} 不可同時有 `[TDD-ALIGN]` 與 `[TDD-RED]`。")
            continue
        if has_align:
            for required in ("TDD-ALIGN", "TDD-GREEN", "TDD-REFACTOR"):
                if required not in found:
                    errors.append(f"{case_id} 缺少 `{required}` 任務。")
            if {"TDD-ALIGN", "TDD-GREEN", "TDD-REFACTOR"} <= found.keys():
                if not (found["TDD-ALIGN"] < found["TDD-GREEN"] < found["TDD-REFACTOR"]):
                    errors.append(f"{case_id} 必須依序為 ALIGN → GREEN → REFACTOR。")
        elif has_red:
            for required in ("TDD-RED", "TDD-GREEN", "TDD-REFACTOR"):
                if required not in found:
                    errors.append(f"{case_id} 缺少 `{required}` 任務。")
            if {"TDD-RED", "TDD-GREEN", "TDD-REFACTOR"} <= found.keys():
                if not (found["TDD-RED"] < found["TDD-GREEN"] < found["TDD-REFACTOR"]):
                    errors.append(f"{case_id} 必須依序為 RED → GREEN → REFACTOR。")
        else:
            errors.append(f"{case_id} 必須以 `[TDD-ALIGN]` 或 `[TDD-RED]` 起鏈。")

        if case_id.startswith("FE-E2E-"):
            first = first_slice_step(found)
            backend_id = infer_backend_id(text, case_id)
            backend = steps.get(backend_id) if backend_id else None
            if first and backend and "TDD-GREEN" in backend:
                if first[1] < backend["TDD-GREEN"]:
                    errors.append(
                        f"{case_id} 的 {first[0]} 不得早於 {backend_id} 的 GREEN。"
                    )


def infer_backend_id(text: str, fe_case_id: str) -> str | None:
    first_block = next(
        (
            block
            for block in task_blocks(text)
            if f"[SLICE {fe_case_id}]" in block.splitlines()[0]
            and ("[TDD-ALIGN]" in block.splitlines()[0] or "[TDD-RED]" in block.splitlines()[0])
        ),
        "",
    )
    mentioned = RE_BACKEND_ID.findall(first_block)
    if mentioned:
        return mentioned[0]
    serial = fe_case_id.replace("FE-E2E-", "BE-API-", 1)
    steps = collect_slice_steps(text)
    return serial if serial in steps else None


def validate_us_action_order(text: str, errors: list[str]) -> None:
    by_us: dict[str, dict[str, list[int]]] = {}
    for match in RE_REMOVE_TASK.finditer(text):
        by_us.setdefault(match.group(1), {}).setdefault("REMOVE", []).append(match.start())
        by_us.setdefault(match.group(1), {}).setdefault("DEV", []).append(match.start())
    for match in RE_REGRESSION_TASK.finditer(text):
        by_us.setdefault(match.group(1), {}).setdefault("REGRESSION", []).append(match.start())
        by_us.setdefault(match.group(1), {}).setdefault("DEV", []).append(match.start())
    for match in RE_SLICE_TASK.finditer(text):
        us_number, step = match.group(1), match.group(3)
        by_us.setdefault(us_number, {}).setdefault("DEV", []).append(match.start())
        if step == "TDD-ALIGN":
            by_us[us_number].setdefault("ALIGN", []).append(match.start())
        elif step == "TDD-RED":
            by_us[us_number].setdefault("RED", []).append(match.start())
    for match in RE_JOURNEY_TASK.finditer(text):
        by_us.setdefault(match.group(1), {}).setdefault("JOURNEY", []).append(match.start())

    for us_number, found in by_us.items():
        remove_pos = min(found["REMOVE"]) if found.get("REMOVE") else None
        regression_pos = min(found["REGRESSION"]) if found.get("REGRESSION") else None
        align_pos = min(found["ALIGN"]) if found.get("ALIGN") else None
        red_pos = min(found["RED"]) if found.get("RED") else None
        journey_pos = min(found["JOURNEY"]) if found.get("JOURNEY") else None
        last_dev = max(found["DEV"]) if found.get("DEV") else None

        if remove_pos is not None and regression_pos is not None and regression_pos < remove_pos:
            errors.append(f"US{us_number} 的 `[REGRESSION]` 不得早於 `[TDD-REMOVE]`。")
        if remove_pos is not None and align_pos is not None and align_pos < remove_pos:
            errors.append(f"US{us_number} 的 ALIGN 不得早於 `[TDD-REMOVE]`。")
        if remove_pos is not None and red_pos is not None and red_pos < remove_pos:
            errors.append(f"US{us_number} 的 RED 不得早於 `[TDD-REMOVE]`。")
        if align_pos is not None and red_pos is not None and red_pos < align_pos:
            errors.append(f"US{us_number} 的 Add／RED 不得早於 Modify／ALIGN。")
        if journey_pos is not None and last_dev is not None and journey_pos < last_dev:
            errors.append(f"US{us_number} 的 Journey Gate 必須在 Delete／Modify／Add 之後。")


def setup_region(text: str) -> str:
    match = re.search(
        r"## Phase 1: 環境建立（Setup）(.*?)## Phase 2: 基礎前置（Foundational）",
        text,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def foundational_region(text: str) -> str:
    match = re.search(
        r"## Phase 2: 基礎前置（Foundational）(.*?)## Phase \d+: User Story",
        text,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def validate_setup_boundary(text: str, errors: list[str]) -> None:
    for label, region in (
        ("Setup", setup_region(text)),
        ("Foundational", foundational_region(text)),
    ):
        if "[SLICE " in region or "[JOURNEY " in region:
            errors.append(f"{label} 不得使用 `[SLICE …]` 或 `[JOURNEY …]` 標題。")
        if re.search(r"建立[^。\n]*tests/run\.php", region):
            errors.append(f"{label} 不得把 `tests/run.php` 寫成要建立的正式 TDD 入口。")


def journey_inside_story_phases(text: str, errors: list[str]) -> None:
    story_spans: list[tuple[int, int, str]] = []
    matches = list(RE_STORY.finditer(text))
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        story_spans.append((start, end, match.group(1)))

    for match in RE_JOURNEY_TASK.finditer(text):
        us_number = match.group(1)
        case_id = match.group(2)
        pos = match.start()
        owner = next((span for span in story_spans if span[0] <= pos < span[1]), None)
        if owner is None:
            errors.append(f"{case_id} 的 ACCEPTANCE-GATE 必須放在所屬 User Story phase 內。")
        elif owner[2] != us_number:
            errors.append(
                f"{case_id} 標成 US{us_number}，但出現在 User Story {owner[2]} phase。"
            )


def notes_section(text: str) -> str | None:
    index = text.find(NOTE_HEADING)
    if index < 0:
        return None
    rest = text[index:]
    next_heading = re.search(r"\n## ", rest[1:])
    return rest[: next_heading.start() + 1] if next_heading else rest


def keep_case_ids(text: str) -> set[str] | None:
    section = notes_section(text)
    if section is None:
        return None
    keep: set[str] = set()
    for line in section.splitlines():
        if re.search(r"\|\s*Keep\s*\|", line):
            keep.update(RE_CASE_ID.findall(line))
    return keep


def validate_against_testplan(
    text: str,
    testplan_text: str | None,
    api_plan_exists: bool,
    errors: list[str],
) -> None:
    if testplan_text is None:
        errors.append("同目錄缺少 `testplan.md`，無法核對切片覆蓋。")
        return

    expected = [match.group(1) for match in RE_TESTPLAN_CASE.finditer(testplan_text)]
    if not expected:
        errors.append("`testplan.md` 沒有可展開的旅程或切片案例。")
        return

    slice_steps = collect_slice_steps(text)
    journey_gates = collect_journey_gates(text)
    keep_ids = keep_case_ids(text)
    uncovered: list[str] = []

    for case_id in expected:
        if "JOURNEY" in case_id:
            if case_id not in journey_gates:
                errors.append(f"testplan 案例 `{case_id}` 缺少 `[ACCEPTANCE-GATE]` 任務。")
        elif case_id.startswith("GLOBAL-NFR-"):
            continue
        else:
            found = slice_steps.get(case_id, {})
            if not found:
                uncovered.append(case_id)
            elif keep_ids is not None and case_id in keep_ids:
                errors.append(f"`{case_id}` 已有切片任務，備註不可再標 Keep。")

    if uncovered:
        if keep_ids is None:
            for case_id in uncovered:
                errors.append(
                    f"testplan 案例 `{case_id}` 缺少工單；Keep 必須在 `{NOTE_HEADING}` 點名，"
                    "否則應展開 ALIGN 或 RED 鏈。"
                )
        else:
            missing_keep = [case_id for case_id in uncovered if case_id not in keep_ids]
            for case_id in missing_keep:
                errors.append(
                    f"testplan 案例 `{case_id}` 沒有切片任務，也未在備註標成 Keep。"
                )

    extra_slices = sorted(set(slice_steps) - set(expected))
    extra_journeys = sorted(set(journey_gates) - set(expected))
    if extra_slices:
        errors.append(f"tasks 出現 testplan 沒有的切片：{', '.join(extra_slices)}")
    if extra_journeys:
        errors.append(f"tasks 出現 testplan 沒有的旅程：{', '.join(extra_journeys)}")

    if api_plan_exists:
        for block in task_blocks(text):
            first_line = block.splitlines()[0]
            if "[SLICE BE-API-" in first_line and any(
                marker in first_line
                for marker in ("[TDD-RED]", "[TDD-GREEN]", "[TDD-ALIGN]")
            ):
                if "api-plan.md" not in block:
                    errors.append(
                        f"後端 ALIGN／RED／GREEN 必讀必須包含 `api-plan.md`：{first_line[:80]}"
                    )


def input_documents_section(text: str) -> str:
    match = re.search(r"\*\*輸入文件\*\*[：:].*?(?=\n## )", text, re.DOTALL)
    return match.group(0) if match else ""


def validate_design_inputs(
    text: str,
    package_dir: Path,
    workspace_root: Path,
    errors: list[str],
) -> None:
    section = input_documents_section(text)
    if not section:
        return
    for relative in DESIGN_INPUT_FILES:
        if (package_dir / relative).is_file() and relative not in section:
            errors.append(f"輸入文件必須列出已存在的 `{relative}`。")
    ui_dir = package_dir / "system-analyze" / "ui"
    if ui_dir.is_dir() and any(ui_dir.glob("*.html")):
        if "system-analyze/ui" not in section:
            errors.append("輸入文件必須列出已存在的 `system-analyze/ui/` 雛形。")
    schema_path = workspace_root / "app" / "config" / "schema.sql"
    if schema_path.is_file() and "schema.sql" not in section:
        errors.append("輸入文件必須列出現行 `app/config/schema.sql`。")


def validate_schema_foundational(
    text: str,
    package_dir: Path,
    workspace_root: Path,
    errors: list[str],
) -> None:
    ddl_path = package_dir / "system-analyze" / "DDL.md"
    if not ddl_path.is_file():
        return
    tables = RE_CREATE_TABLE.findall(ddl_path.read_text(encoding="utf-8"))
    if not tables:
        return
    schema_path = workspace_root / "app" / "config" / "schema.sql"
    schema_text = schema_path.read_text(encoding="utf-8") if schema_path.is_file() else ""
    missing = [name for name in tables if name not in schema_text]
    if not missing:
        return
    if "schema.sql" not in foundational_region(text):
        errors.append(
            "DDL.md 的資料表 "
            + ", ".join(missing)
            + " 尚未出現在 app/config/schema.sql，Foundational 必須有落地 schema.sql 的任務。"
        )


def main() -> int:
    args = parse_args()
    try:
        tasks_path, testplan_path, api_plan_path, package_dir, workspace_root = (
            resolve_paths(args)
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        text = load_text(tasks_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    testplan_text = None
    if testplan_path is not None and testplan_path.exists():
        testplan_text = testplan_path.read_text(encoding="utf-8")

    errors: list[str] = []
    validate_document(text, errors)
    validate_headings(text, errors)
    validate_task_fields(text, errors)
    validate_slice_chains_and_order(text, errors)
    validate_us_action_order(text, errors)
    validate_setup_boundary(text, errors)
    journey_inside_story_phases(text, errors)
    validate_against_testplan(text, testplan_text, api_plan_path.exists(), errors)
    validate_design_inputs(text, package_dir, workspace_root, errors)
    validate_schema_foundational(text, package_dir, workspace_root, errors)

    if errors:
        print("TASKS VALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("TASKS VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
