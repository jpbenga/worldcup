import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { DataSourceType, Match } from '../models/worldcup.models';

interface BackendMatch {
  match_id: string;
  home_team: string;
  away_team: string;
  kickoff_at: string;
  competition: string;
  stage: string;
  group?: string;
  status: Match['status'];
  home_score?: number;
  away_score?: number;
  source_type: DataSourceType;
  source_name: string;
  is_real_fixture: boolean;
  is_future_fixture?: boolean;
}

@Injectable({ providedIn: 'root' })
export class MatchService {
  private readonly http = inject(HttpClient);

  getMatches(): Observable<Match[]> {
    return this.http.get<BackendMatch[]>('assets/data/matches.json').pipe(
      map((matches) =>
        matches.map((match) => ({
          id: match.match_id,
          homeTeam: match.home_team,
          awayTeam: match.away_team,
          kickoffAt: match.kickoff_at,
          competition: match.competition,
          stage: match.stage,
          group: match.group,
          status: match.status,
          homeScore: match.home_score,
          awayScore: match.away_score,
          sourceType: match.source_type,
          sourceName: match.source_name,
          isRealFixture: match.is_real_fixture,
          isFutureFixture: match.is_future_fixture,
        })),
      ),
    );
  }
}
