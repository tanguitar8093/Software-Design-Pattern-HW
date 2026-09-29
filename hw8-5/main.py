import sys

from v1.app.driver import AppDriver


def main() -> None:
    lines = sys.stdin.read().splitlines()
    driver = AppDriver()
    for line in driver.run(lines):
        print(line)


if __name__ == "__main__":
    main()
