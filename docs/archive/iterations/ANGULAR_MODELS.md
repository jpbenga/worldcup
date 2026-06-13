# Modèles Angular

## Interfaces TypeScript

Ces interfaces représentent le modèle utilisé par Angular après conversion des
JSON backend en `snake_case`.

```ts
export interface Match {
  id: string;
  homeTeam: string;
  awayTeam: string;
  kickoffAt: string;
  competition: string;
  stage: string;
  group?: string;
  status: 'scheduled' | 'live' | 'finished';
  homeScore?: number;
  awayScore?: number;
}

export interface ScoreProbability {
  score: string;
  homeGoals: number;
  awayGoals: number;
  probability: number;
}

export interface ScoreMatrix {
  matchId: string;
  maxGoals: number;
  probabilities: ScoreProbability[];
}

export interface MatchMarkets {
  homeWin: number;
  draw: number;
  awayWin: number;
  homeOrDraw: number;
  awayOrDraw: number;
  noDraw: number;
  over05: number;
  over15: number;
  over25: number;
  over35: number;
  under25: number;
  under35: number;
  bttsYes: number;
  bttsNo: number;
}

export interface MatchPrediction {
  matchId: string;
  generatedAt: string;
  version: string;
  scoreMatrix: ScoreMatrix;
  markets: MatchMarkets;
  confidence: 'low' | 'medium' | 'high';
  topScores: ScoreProbability[];
}

export interface BacktestResult {
  matchId: string;
  marketName: string;
  predictedProbability: number;
  actualResult: boolean;
  validated: boolean;
  evaluatedAt: string;
}
```

Pour afficher un historique reproductible, l'implémentation Angular pourra
étendre `BacktestResult` avec `predictionVersion`, `generatedAt` et le score
réel, déjà prévus dans le contrat backend.

## Conversion depuis les JSON

Le backend conserve les clés `snake_case`. Les services Angular les convertissent
une seule fois en `camelCase` à la lecture. Exemples :

| JSON backend | Angular |
|---|---|
| `match_id` | `id` pour `Match`, sinon `matchId` |
| `home_team` | `homeTeam` |
| `kickoff_at` | `kickoffAt` |
| `prediction_version` | `version` |
| `score_matrix` | `scoreMatrix` |
| `over_2_5` | `over25` |
| `btts_yes` | `bttsYes` |

La conversion peut être assurée par de petites fonctions mapper dans les
services. Angular ne doit pas recalculer les probabilités ni les marchés.

## Composants proposés

| Composant | Responsabilité |
|---|---|
| `HomeComponent` | Vue d'entrée personnelle, prochains matchs et accès aux simulations |
| `MatchListComponent` | Liste et filtres de matchs |
| `MatchCardComponent` | Résumé d'un match et probabilités principales |
| `MatchDetailComponent` | Composition du détail d'un match |
| `ScoreMatrixComponent` | Affichage lisible de la matrice et des top scores |
| `MarketSummaryComponent` | Affichage 1X2, doubles chances, over/under et BTTS |
| `PredictionHistoryComponent` | Historique complet des validations et échecs |
| `TournamentSimulationComponent` | Résumé des scénarios de tournoi, une fois le moteur disponible |
| `ResponsibleNoticeComponent` | Transparence, limites et avertissement responsable |

Pour rester simple, commencer avec des composants standalone et des routes
`/`, `/matches`, `/matches/:id`, `/history` et `/simulation`.

## Services proposés

| Service | Responsabilité |
|---|---|
| `MatchService` | Charger, filtrer et joindre matchs et résultats |
| `PredictionService` | Charger les snapshots et retourner la version demandée |
| `BacktestingService` | Charger et filtrer l'historique des validations |
| `SimulationService` | Charger les sorties du simulateur de tournoi |
| `DataExportService` | Exporter les vues personnelles en JSON ou CSV |

Les services lisent d'abord des fichiers JSON statiques depuis
`public/data/`. Une petite API pourra remplacer ces URLs plus tard sans changer
les composants.

## Première découpe Angular utile

```text
frontend/src/app/
├── core/
│   ├── models/
│   ├── mappers/
│   └── services/
├── features/
│   ├── matches/
│   ├── prediction-history/
│   └── tournament-simulation/
└── shared/
    └── responsible-notice/
```

La première tranche doit seulement charger `matches.json` et
`predictions.json`, afficher la liste, ouvrir un détail, puis présenter matrice
et marchés.
