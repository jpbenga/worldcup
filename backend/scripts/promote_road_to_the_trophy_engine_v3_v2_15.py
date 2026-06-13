import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.road_to_the_trophy_v3_promotion_pipeline_v2_15 import promote
promote()
