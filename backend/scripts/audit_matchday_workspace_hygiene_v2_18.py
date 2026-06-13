import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.unified_local_refresh_utils_v2_18 import ROOT, publish
from backend.scripts.pipeline_utils import utc_now

lines = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
rows = []
for line in lines:
    path = line[3:]
    related = any(token in path for token in ("matchday", "worldcup_", "prediction", "result_", "dual_matrix", "data_sources"))
    tracked = not line.startswith("??")
    rows.append({"path": path, "git_status": line[:2], "refresh_related": related, "tracked": tracked, "classification": "expected_local_refresh" if related else "iteration_or_unrelated", "recommendation": "review_before_commit" if related else "keep_out_of_scope"})
payload = {"version": "v2.18", "generated_at": utc_now(), "dirty": bool(rows), "files": rows, "expected_refresh_files": [r["path"] for r in rows if r["refresh_related"]], "unexpected_dirty_files": [r["path"] for r in rows if not r["refresh_related"]], "automatic_deletion": False}
publish("matchday_workspace_hygiene_audit_v2_18.json", payload)
print(f"Workspace hygiene: dirty={payload['dirty']}; expected_refresh={len(payload['expected_refresh_files'])}; other={len(payload['unexpected_dirty_files'])}")
