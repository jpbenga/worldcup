"""Audit prediction diffs after the V2.30.1 full-stats promotion."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import large_win_probability
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.30.1"
OUTPUT = "full_stats_promotion_diff_v2_30_1.json"
PREVIOUS = DATA_DIR / "archives" / "v2_30_1_pre_full_stats_promotion" / "predictions.generated.json"
PROMOTED = DATA_DIR / "generated" / "predictions.json"
REQUIRED = ("match_id", "home_team", "away_team", "markets", "score_matrix")


def publish(payload: dict[str, Any]) -> None:
    for base in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        write_json(payload, base / OUTPUT)


def market_shift(old: dict[str, Any], new: dict[str, Any]) -> float:
    return max(
        abs(float(old["markets"][key]) - float(new["markets"][key]))
        for key in ("home_win", "draw", "away_win")
    )


def mode_score(row: dict[str, Any]) -> str | None:
    scores = row.get("top_scores") or []
    if scores:
        return str(scores[0].get("score"))
    matrix = row.get("score_matrix", {})
    items = matrix.get("probabilities", []) if isinstance(matrix, dict) else matrix
    if not items:
        return None
    best = max(items, key=lambda item: float(item.get("probability", 0.0)))
    return best.get("score") or f"{best.get('home_goals')}-{best.get('away_goals')}"


def main() -> None:
    previous = load_json(PREVIOUS)
    promoted = load_json(PROMOTED)
    previous_by_id = {row["match_id"]: row for row in previous}
    promoted_by_id = {row["match_id"]: row for row in promoted}
    blocking = []
    if set(previous_by_id) != set(promoted_by_id):
        blocking.append("fixture_ids_do_not_match")
    shifts = []
    top_changed = []
    score_changes = 0
    large_changes = []
    schema_ok = True
    odds_presence_unchanged = True
    for match_id in sorted(set(previous_by_id) & set(promoted_by_id)):
        old, new = previous_by_id[match_id], promoted_by_id[match_id]
        if old.get("home_team") != new.get("home_team") or old.get("away_team") != new.get("away_team"):
            blocking.append(f"team_mismatch:{match_id}")
        if not all(key in new for key in REQUIRED):
            schema_ok = False
        if bool(old.get("odds")) != bool(new.get("odds")):
            odds_presence_unchanged = False
        shift = market_shift(old, new)
        shifts.append(shift)
        old_mode, new_mode = mode_score(old), mode_score(new)
        score_changed = old_mode != new_mode
        score_changes += int(score_changed)
        large_delta = large_win_probability(new) - large_win_probability(old)
        large_changes.append(abs(large_delta))
        top_changed.append({
            "match_id": match_id,
            "match_label": f"{old.get('home_team')} - {old.get('away_team')}",
            "probability_shift": round(shift, 6),
            "previous_mode_score": old_mode,
            "promoted_mode_score": new_mode,
            "mode_score_changed": score_changed,
            "large_win_probability_delta": round(large_delta, 6),
            "previous_markets": {key: old["markets"][key] for key in ("home_win", "draw", "away_win")},
            "promoted_markets": {key: new["markets"][key] for key in ("home_win", "draw", "away_win")},
        })
    if not schema_ok:
        blocking.append("schema_incompatible")
    if not odds_presence_unchanged:
        blocking.append("odds_presence_changed")
    payload = {
        "version": VERSION,
        "generated_at": utc_now(),
        "fixtures_match": set(previous_by_id) == set(promoted_by_id),
        "match_count_previous": len(previous),
        "match_count_promoted": len(promoted),
        "average_probability_shift": round(sum(shifts) / len(shifts), 6) if shifts else None,
        "max_probability_shift": round(max(shifts), 6) if shifts else None,
        "score_repere_changes": score_changes,
        "average_large_win_probability_shift": round(sum(large_changes) / len(large_changes), 6) if large_changes else None,
        "top_changed_matches": sorted(top_changed, key=lambda row: row["probability_shift"], reverse=True)[:12],
        "schema_compatible": schema_ok,
        "odds_presence_unchanged": odds_presence_unchanged,
        "blocking_issues": blocking,
    }
    publish(payload)
    print(f"{VERSION} promotion diff audit: {'PASS' if not blocking else 'FAIL'}")
    if blocking:
        raise SystemExit(blocking)


if __name__ == "__main__":
    main()
