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

REQUIRED_SECTIONS = [
    "## 每階段產物盤點表",
    "## 攔截檢查",
    "## 問題總表",
    "## 規格覆蓋矩陣（需求 → 實際介面 → Slice → Task → Journey）",
    "## 驗收覆蓋矩陣（GWT／邊界 → Slice → Journey）",
    "## 指標",
    "## 其餘發現摘要",
    "## 下一步建議",
    "## 假設",
]

REQUIRED_INTERCEPTS = [
    "缺切片（Slice）／任務（Task）／跨端旅程（Journey）",
    "GWT 缺失",
    "Mock 前端階段",
    "固定三層（後端／前端／整合）",
    "`BE-REPO-*`",
    "舊三檔 task",
    "既有測試動作鏈",
    "DDL／schema 工單",
]

FORBIDDEN_REQUIRED_PATHS = [
    "e2e-test-plan.md",
    "task-plan/task-backend.md",
    "task-plan/task-frontend.md",
    "task-plan/task-integration.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="檢查 analyze-report 產出的結構是否有效。")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="要直接檢查的 analyze-report Markdown 檔案路徑")
    group.add_argument(
        "--package",
        help="要檢查的 NNN-plan-package；預設對應 specs/<package>/analyze-report.md",
    )
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="workspace 根目錄；使用 --package 時會從此目錄推導 specs/<package>/analyze-report.md",
    )
    return parser.parse_args()


def resolve_path(args: argparse.Namespace) -> Path:
    if args.input:
        return Path(args.input)
    assert args.package is not None
    if not RE_PACKAGE_NAME.match(args.package):
        raise ValueError(
            f"Invalid package name: {args.package}. Expected format like 001-overtime-correction"
        )
    return Path(args.workspace_root) / "specs" / args.package / "analyze-report.md"


def section_after(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading) :]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    return rest if next_heading is None else rest[: next_heading.start()]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    args = parse_args()
    try:
        report_path = resolve_path(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not report_path.is_file():
        print(f"找不到分析報告：{report_path}", file=sys.stderr)
        return 1

    text = report_path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("# 規格分析報告："):
        fail(errors, "H1 必須是「# 規格分析報告：…」")
    if "**功能分支**:" not in text:
        fail(errors, "缺少小標 **功能分支**:")
    if "無嚴重發現，不阻擋" in text and "無可修項" not in text:
        fail(errors, "下一步建議應使用「無可修項」，不要再用「無嚴重發現，不阻擋」當放行語")
    if RE_PLACEHOLDER.search(text):
        fail(errors, "報告仍含未填的 {{PLACEHOLDER}}")
    if "my-specify" in text:
        fail(errors, "報告不得再寫 my-specify；指令名是 /specify")

    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            fail(errors, f"缺少章節：{heading}")

    inventory = section_after(text, "## 每階段產物盤點表")
    for required in ("spec.md", "testplan.md", "tasks.md"):
        if required not in inventory:
            fail(errors, f"產物盤點表必須列出必備 {required}")
        if "必備" not in inventory:
            fail(errors, "產物盤點表必須標示「必備」角色")
            break
    for forbidden in FORBIDDEN_REQUIRED_PATHS:
        for line in inventory.splitlines():
            if forbidden in line and "必備" in line:
                fail(errors, f"不可把 {forbidden} 列為必備：{line.strip()}")

    intercept = section_after(text, "## 攔截檢查")
    for label in REQUIRED_INTERCEPTS:
        if label not in intercept:
            fail(errors, f"攔截檢查缺少：{label}")

    coverage = section_after(text, "## 規格覆蓋矩陣")
    for column in ("實際介面", "切片（Slice）", "任務（Task）", "旅程（Journey）"):
        if column not in coverage:
            fail(errors, f"規格覆蓋矩陣缺少欄位：{column}")
    if re.search(r"\|\s*Scenario\s*\|", coverage):
        fail(errors, "規格覆蓋矩陣不可再使用 Scenario 欄")

    acceptance = section_after(text, "## 驗收覆蓋矩陣")
    if re.search(r"\|\s*後端\s*\|\s*前端\s*\|\s*整合\s*\|", acceptance):
        fail(errors, "驗收覆蓋矩陣不可再使用後端／前端／整合三欄")
    if "| 切片（Slice） |" not in acceptance and "切片（Slice）" not in acceptance:
        fail(errors, "驗收覆蓋矩陣必須有切片（Slice）欄")
    if "旅程（Journey）" not in acceptance:
        fail(errors, "驗收覆蓋矩陣必須有旅程（Journey）欄")

    next_section = section_after(text, "## 下一步建議")
    list_items = [
        line.strip()
        for line in next_section.splitlines()
        if re.match(r"^(?:- |\d+\.\s+)\S", line.strip())
    ]
    if not list_items:
        fail(errors, "下一步建議必須使用 `-` 或編號條列，不可只寫散文")

    next_joined = "\n".join(list_items)
    if "請自行檢查" in next_section or "手動修改" in next_section:
        fail(errors, "下一步建議不得寫「請自行檢查」或「手動修改」來源檔")
    if "無可修項" in next_joined:
        if "/implement" not in next_joined:
            fail(errors, "無可修項時，下一步必須寫明進入 /implement")
    else:
        skill_hits = re.findall(
            r"/(?:specify|testplan|tasks|implement|analyze|api-plan|ui-plan|data-plan|system-analyze|clarify)",
            next_joined,
        )
        if not skill_hits:
            fail(
                errors,
                "有可修項時，下一步每條必須點名要呼叫的 skill 與範圍",
            )

    if re.search(r"^## (後端|前端|整合)\s*$", text, re.MULTILINE):
        fail(errors, "報告不可再以 ## 後端／前端／整合 當第一層章節")

    if errors:
        print("analyze-report 驗證失敗：", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print(f"analyze-report 驗證通過：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
