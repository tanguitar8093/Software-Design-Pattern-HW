#!/bin/bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTCASE_DIR="$SCRIPT_DIR/testcases"

echo "=== 開始執行測試 ==="
for test in "$TESTCASE_DIR"/*.in; do
    out="${test%.in}.out"
    actual="actual_$(basename "$out")"
    python3 "$SCRIPT_DIR/main.py" < "$test" > "$actual" 2>&1
    
    if diff -u "$out" "$actual" > "diff_$(basename "$test").log"; then
        echo "✅ 通過: $(basename "$test")"
        rm "$actual" "diff_$(basename "$test").log"
    else
        echo "❌ 失敗: $(basename "$test") (請查看 diff_$(basename "$test").log)"
    fi
done
echo "=== 測試結束 ==="
