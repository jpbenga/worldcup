import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.operator_utils_v2_17 import freshness_status, publish

status = freshness_status()
publish("data_freshness_status_v2_17.json", status, frontend=True)
print(f"Data freshness: {status['data_status'].upper()}; last refresh={status['last_matchday_refresh_at']}")
