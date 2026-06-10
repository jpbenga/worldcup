import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { BacktestResult } from '../models/worldcup.models';

interface BackendBacktestResult {
  match_id: string;
  market_name: string;
  predicted_probability: number;
  actual_result: boolean;
  validated: boolean;
  evaluated_at: string;
}

interface BackendBacktestResponse {
  results: BackendBacktestResult[];
}

@Injectable({ providedIn: 'root' })
export class BacktestingService {
  private readonly http = inject(HttpClient);

  getResults(): Observable<BacktestResult[]> {
    return this.http.get<BackendBacktestResponse>('assets/data/backtest_results.json').pipe(
      map(({ results }) =>
        results.map((result) => ({
          matchId: result.match_id,
          marketName: result.market_name,
          predictedProbability: result.predicted_probability,
          actualResult: result.actual_result,
          validated: result.validated,
          evaluatedAt: result.evaluated_at,
        })),
      ),
    );
  }
}
