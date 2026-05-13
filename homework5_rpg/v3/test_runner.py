import subprocess
import sys
from pathlib import Path


def run_test(in_file_path: str | Path) -> None:
    in_path = Path(in_file_path)
    if not in_path.exists() or in_path.suffix != ".in":
        print(f"[-1] 找不到測資檔案或格式錯誤: {in_file_path}")
        return

    test_name = in_path.stem
    expected_out_path = in_path.with_suffix(".out")
    actual_out_path = Path(f"actual_{test_name}.out")

    with in_path.open("r", encoding="utf-8") as infile, actual_out_path.open("w", encoding="utf-8") as outfile:
        subprocess.run(
            [sys.executable, "main.py"],
            stdin=infile,
            stdout=outfile,
            stderr=subprocess.STDOUT,
            check=False,
        )

    if not expected_out_path.exists():
        print(f"⚠️ [{test_name}] 測試結束 (無 {expected_out_path.name} 預期輸出檔案可供比對)")
        return

    with expected_out_path.open("r", encoding="utf-8") as file:
        expected_lines = [line.rstrip() for line in file.readlines()]

    with actual_out_path.open("r", encoding="utf-8") as file:
        actual_lines = [line.rstrip() for line in file.readlines()]

    if expected_lines == actual_lines:
        print(f"✅ 通過: {test_name}")
    else:
        print(f"❌ 失敗: {test_name} (實際輸出在 {actual_out_path})")


def main() -> None:
    if len(sys.argv) < 2:
        print("請提供要測試的測資路徑。")
        print("測試單一測資: python3 test_runner.py testcases/summon.in")
        print("測試所有測資: python3 test_runner.py all")
        sys.exit(1)

    arg = sys.argv[1]

    if arg.lower() == "all":
        testcases_dir = Path("testcases")
        if not testcases_dir.exists():
            print("找不到 testcases 資料夾")
            sys.exit(1)

        in_files = sorted(testcases_dir.glob("*.in"))
        if not in_files:
            print("沒有找到任何 .in 測資")
            sys.exit(1)

        print(f"=== 執行所有測資 (共 {len(in_files)} 個) ===")
        for in_file in in_files:
            run_test(in_file)
        print("========================")
    else:
        run_test(arg)


if __name__ == "__main__":
    main()
