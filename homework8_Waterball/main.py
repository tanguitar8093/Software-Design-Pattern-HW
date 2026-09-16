"""
homework8_Waterball 進入點轉發模組：
將呼叫委託至同目錄下 v1.main。
"""
import sys
from pathlib import Path

cur_dir = Path(__file__).resolve().parent
if str(cur_dir) not in sys.path:
    sys.path.insert(0, str(cur_dir))

from v1.main import (
    CommunitySimulationDriver,
    run_simulation,
)

if __name__ == "__main__":
    from v1.main import main as v1_main
    v1_main()
