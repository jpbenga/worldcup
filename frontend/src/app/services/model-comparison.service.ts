import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, Observable, of } from 'rxjs';
import { ModelComparison } from '../models/worldcup.models';

interface BackendModelComparison {
  match_id: string;
  baseline_model_version: string;
  elo_model_version: string;
  home_team?: string;
  away_team?: string;
  elo_available: boolean;
  home_elo?: number;
  away_elo?: number;
  deltas: {
    home_win: number;
    draw: number;
    away_win: number;
    over_2_5?: number;
    btts_yes?: number;
  };
  baseline_top_score?: string;
  elo_top_score?: string;
  impact_level: ModelComparison['impactLevel'];
}

@Injectable({ providedIn: 'root' })
export class ModelComparisonService {
  private readonly http = inject(HttpClient);

  getComparisons(): Observable<ModelComparison[]> {
    return this.http.get<BackendModelComparison[]>('assets/data/model_comparison.json').pipe(
      map((items) =>
        items.map((item) => ({
          matchId: item.match_id,
          baselineModelVersion: item.baseline_model_version,
          eloModelVersion: item.elo_model_version,
          homeTeam: item.home_team,
          awayTeam: item.away_team,
          eloAvailable: item.elo_available,
          homeElo: item.home_elo,
          awayElo: item.away_elo,
          deltas: {
            homeWin: item.deltas.home_win,
            draw: item.deltas.draw,
            awayWin: item.deltas.away_win,
            over25: item.deltas.over_2_5,
            bttsYes: item.deltas.btts_yes,
          },
          baselineTopScore: item.baseline_top_score,
          eloTopScore: item.elo_top_score,
          impactLevel: item.impact_level,
        })),
      ),
      catchError(() => of([])),
    );
  }
}
