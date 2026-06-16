"""Build the French algorithm-readiness answer and the single V2.27.1 report."""

from __future__ import annotations

import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "api_stats_algorithm_readiness_answer_v2_27_1.json"
REPORT = ROOT / "docs" / "API_FOOTBALL_HISTORICAL_COVERAGE_AUDIT_V2_27_1.md"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f} %".replace(".", ",")


def status(rate: float | None) -> str:
    if rate is None or rate < 0.5:
        return "not_ready"
    if rate < 0.8:
        return "fragile"
    return "promising"


def main() -> None:
    discovery = load_json(DATA_DIR / "generated" / "historical_competition_coverage_v2_27_1.json")
    sample = load_json(DATA_DIR / "generated" / "historical_api_sample_fixtures_v2_27_1.json")
    audit = load_json(DATA_DIR / "generated" / "api_football_historical_stats_coverage_v2_27_1.json")
    matrix = load_json(DATA_DIR / "generated" / "api_football_historical_coverage_matrix_v2_27_1.json")
    summary = matrix["global_summary"]
    can_backtest = all((summary[key] or 0) >= 0.9 for key in ("statistics_global_rate", "events_global_rate", "lineups_global_rate", "players_global_rate")) and summary["competition_seasons_checked"] >= discovery["local_historical_dataset"]["competition_seasons_count"]
    families = {
        "xg": (summary["xg_global_rate"], "Les xG sont post-match et leur couverture historique varie; ils ne sont pas prêts pour un backtest global."),
        "shots": (audit["coverage_summary"]["shots_available_rate"], "Les tirs sont utiles pour expliquer la performance et créer plus tard des agrégats retardés."),
        "possession": (audit["coverage_summary"]["possession_available_rate"], "La possession est exploitable en explication, sous réserve de valeurs manquantes."),
        "events": (summary["events_global_rate"], "Les événements permettent l'explication et un futur moteur live séparé."),
        "lineups": (summary["lineups_global_rate"], "Les compositions nécessitent une preuve d'horodatage pré-match avant tout usage prédictif."),
        "players": (summary["players_global_rate"], "Les statistiques joueurs sont riches mais souvent nulles et post-match."),
    }
    payload = {
        "version": "v2.27.1",
        "answer": {
            "short_answer": "API-Football enrichit de façon crédible l'explication post-match historique, mais cet échantillon stratifié ne suffit pas à autoriser des features globales ou un backtest historique sans biais.",
            "can_use_for_historical_backtest": can_backtest,
            "can_use_for_post_match_explanation": (summary["statistics_global_rate"] or 0) >= 0.5,
            "can_use_for_future_model_features": False,
            "can_use_for_live_model": False,
            "main_blockers": [
                "Seulement cinq fixtures stratifiées par compétition ont été testées pour respecter le quota.",
                "La couverture n'est pas prouvée pour chacun des 32 couples compétition-saison.",
                "Les valeurs nulles et l'évolution méthodologique du fournisseur doivent être auditées.",
                "Les statistiques et joueurs sont post-match; les compositions exigent une provenance temporelle stricte.",
            ],
            "safe_next_steps": [
                "Utiliser d'abord les données comme couche explicative post-match.",
                "Étendre l'audit par lots cache-first à chaque compétition-saison.",
                "Créer des agrégats retardés seulement sur les périodes couvertes et les tester chronologiquement.",
                "Conserver le moteur live séparé de la prédiction pré-match gelée.",
            ],
        },
        "by_data_family": {name: {"status": status(rate), "explanation": explanation} for name, (rate, explanation) in families.items()},
        "recommended_strategy": [
            "V2.28A: explication post-match historique avec indicateur de disponibilité.",
            "V2.28B: audit exhaustif de couverture et stabilité par compétition-saison.",
            "V2.28C: challenger de features retardées sans fuite, limité aux segments validés.",
        ],
    }
    publish(payload)
    states = Counter(row["algorithm_feature_readiness"] for row in matrix["matrix"])
    rows = "\n".join(
        f"| {row['competition']} | {row['season_or_year']} | {row['sample_size']} | {pct(row['statistics_available_rate'])} | {pct(row['xg_available_rate'])} | {pct(row['events_available_rate'])} | {pct(row['lineups_available_rate'])} | {pct(row['players_available_rate'])} | {row['algorithm_feature_readiness']} |"
        for row in matrix["matrix"]
    )
    REPORT.write_text(
        f"""# V2.27.1 — Audit de couverture historique API-Football

## Contexte utilisateur

V2.27 avait démontré une couverture riche sur trois matchs récents, sans prouver que les mêmes données existaient sur l'historique utilisé par SimuMondial. Cet audit mesure un échantillon historique contrôlé avant toute création de feature modèle.

## Résumé exécutif

Le dataset actif contient `{discovery['local_historical_dataset']['matches_count']}` matchs, `{discovery['local_historical_dataset']['competitions_count']}` compétitions et `{discovery['local_historical_dataset']['competition_seasons_count']}` couples compétition-saison. Tous les matchs locaux sont déjà mappés à un fixture ID API-Football.

Tester cinq matchs pour chaque couple aurait demandé `{sample['sampling_policy']['ideal_api_calls']}` appels. Pour respecter le plafond, l'audit a sélectionné `{len(sample['selected_fixtures'])}` matchs, cinq par compétition, stratifiés de l'ancien au récent. Il a utilisé `{audit['live_calls_used']}` appels live et `{audit['cache_hits']}` réponses en cache.

Conclusion: API-Football est utilisable maintenant pour une couche explicative post-match avec gestion explicite de la disponibilité. La couverture n'est pas encore suffisamment démontrée pour enrichir globalement l'algorithme ou conduire un backtest historique sans biais de sélection.

## Compétitions et années détectées

- Compétitions: {', '.join(discovery['local_historical_dataset']['competitions'])}
- Années/saisons: {', '.join(discovery['local_historical_dataset']['years'])}
- Plage de dates: `{discovery['local_historical_dataset']['date_range']['min']}` à `{discovery['local_historical_dataset']['date_range']['max']}`
- Mapping fixture ID: `{discovery['local_historical_dataset']['matches_with_api_football_fixture_id']}/{discovery['local_historical_dataset']['matches_count']}`

## Méthode d'échantillonnage

Le script découvre automatiquement le dataset local et tente d'abord jusqu'à cinq fixtures par compétition-saison. Le besoin idéal dépassant le quota, il applique le fallback documenté: cinq fixtures régulièrement espacées dans l'historique de chaque compétition. Les endpoints prioritaires sont `fixtures/statistics`, `fixtures/events`, `fixtures/lineups` et `fixtures/players`; aucune recherche ambiguë de fixture n'est nécessaire.

## Couverture globale observée

- Statistiques match: `{pct(summary['statistics_global_rate'])}`
- xG: `{pct(summary['xg_global_rate'])}`
- Events: `{pct(summary['events_global_rate'])}`
- Lineups: `{pct(summary['lineups_global_rate'])}`
- Statistiques joueurs: `{pct(summary['players_global_rate'])}`
- États agrégés: `{dict(states)}`

## Matrice de couverture

| Compétition | Saison | N | Stats | xG | Events | Lineups | Joueurs | Readiness |
|---|---:|---:|---:|---:|---:|---:|---:|---|
{rows}

## Disponibilité et limites

Les statistiques match mesurent tirs, possession, corners, passes et arrêts lorsqu'elles sont présentes. Les xG sont conservés comme absents lorsqu'ils ne sont pas renvoyés; aucune valeur n'est inventée. Les événements sont comparés au total de buts local comme contrôle minimal. Les compositions et statistiques joueurs sont mesurées séparément, avec leurs champs nuls.

L'échantillon couvre l'ancien, le milieu et le récent de chaque compétition, mais pas chaque saison. Les différences par saison restent donc indicatives et non exhaustives. Les flags de couverture fournisseur et cinq fixtures réussies ne suffisent pas à prouver une stabilité historique complète.

## Exploitabilité algorithme

- Backtest historique global: **non**, couverture par compétition-saison encore insuffisamment prouvée.
- Explication post-match: **oui**, avec fallback et indicateur de disponibilité.
- Futures features: **pas encore**; uniquement après audit exhaustif, agrégats retardés et backtest chronologique.
- Live: **pas encore**; nécessite une étude distincte des snapshots et délais.

## Recommandations V2.28

1. Livrer une couche post-match qui n'affiche que les champs réellement disponibles.
2. Étendre l'audit cache-first par lots à chacun des 32 couples compétition-saison.
3. Mesurer les valeurs nulles et ruptures de définition par année.
4. Construire ensuite un challenger de features retardées, limité aux segments validés et sans fuite temporelle.

## Prudences

Aucun moteur, aucune prédiction active, aucun entraînement, aucune exécution Optuna et aucun composant UI fonctionnel ne sont modifiés. Les réponses API brutes restent locales et hors commit.
""",
        encoding="utf-8",
    )
    print(f"V2.27.1 algorithm readiness answer: backtest={can_backtest}, post_match={payload['answer']['can_use_for_post_match_explanation']}")


if __name__ == "__main__":
    main()
