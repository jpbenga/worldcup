import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.unified_local_refresh_utils_v2_18 import publish, refresh_decision

parser = argparse.ArgumentParser()
parser.add_argument("--simulations", type=int, default=50000)
parser.add_argument("--force", action="store_true")
args = parser.parse_args()
decision = refresh_decision(args.simulations, args.force)
publish("local_refresh_needed_v2_18.json", decision)
print(f"Local refresh needed: {decision['refresh_needed']}; reasons={decision['reasons']}")
