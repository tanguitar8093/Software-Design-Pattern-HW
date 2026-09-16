import sys
from pathlib import Path

# 將 workspace 根目錄加入 sys.path
workspace_dir = Path(__file__).parent.parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))
