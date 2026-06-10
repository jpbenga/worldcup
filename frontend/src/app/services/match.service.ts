import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Match } from '../models/worldcup.models';

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
}

@Injectable({ providedIn: 'root' })
export class MatchService {
  private readonly http = inject(HttpClient);

  getMatches(): Observable<Match[]> {
    return this.http.get<BackendMatch[]>('assets/data/sample_matches.json').pipe(
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
        })),
      ),
    );
  }
}
