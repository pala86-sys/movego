"""測試共用設定：把 backend/ 加進 import path，讓 `import app...` 可運作。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
