import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTER_DIR = ROOT / "starter"

if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))
