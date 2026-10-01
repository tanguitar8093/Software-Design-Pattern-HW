import sys
from pathlib import Path

# 直接執行入口檔時，讓 Python 能找到 hw8-5 下的版本套件。
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from v2.app.driver import AppDriver


def main() -> None:
    lines = sys.stdin.read().splitlines()
    driver = AppDriver()
    for line in driver.run(lines):
        print(line)


if __name__ == "__main__":
    main()
