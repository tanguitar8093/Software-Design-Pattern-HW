import sys
from pathlib import Path

# 將 v1 目錄加入 sys.path，保證 tests 無論隨 v1 移動到任何位置，都能直接 import main 或其子套件
v1_dir = Path(__file__).resolve().parent.parent
if str(v1_dir) not in sys.path:
    sys.path.insert(0, str(v1_dir))

parent_dir = v1_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
