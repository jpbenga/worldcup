import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.tournament_simulation_engine_v3_pipeline_v2_14 import build_all
build_all()
