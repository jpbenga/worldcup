import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import {
  MatchMarkets,
  MatchPrediction,
  DataSourceType,
  ReleaseCandidatePrediction,
  ScoreMatrix,
  ScoreProbability,
} from '../models/worldcup.models';

interface BackendScoreProbability {
  score: string;
  home_goals: number;
  away_goals: number;
  probability: number;
}

interface BackendScoreMatrix {
  match_id: string;
  max_goals: number;
  probabilities: BackendScoreProbability[];
}

interface BackendMarkets {
  home_win: number;
  draw: number;
  away_win: number;
  home_or_draw: number;
  away_or_draw: number;
  no_draw: number;
  over_0_5: number;
  over_1_5: number;
  over_2_5: number;
  over_3_5: number;
  under_2_5: number;
  under_3_5: number;
  btts_yes: number;
  btts_no: number;
}

interface BackendPrediction {
  prediction_id: string;
  match_id: string;
  generated_at: string;
  model_version: string;
  prediction_version: string;
  data_source_type: DataSourceType;
  is_real_data: boolean;
  score_matrix: BackendScoreMatrix;
  markets: BackendMarkets;
  confidence: MatchPrediction['confidence'];
  top_scores: BackendScoreProbability[];
}

@Injectable({ providedIn: 'root' })
export class PredictionService {
  private readonly http = inject(HttpClient);

  getPredictions(): Observable<MatchPrediction[]> {
    return this.getFromSnapshot('predictions.json');
  }

  getEloPredictions(): Observable<MatchPrediction[]> {
    return this.getFromSnapshot('predictions_elo.json');
  }

  getReleaseCandidatePredictions(): Observable<ReleaseCandidatePrediction[]> {
    return this.http
      .get<any>('assets/data/worldcup_2026_predictions_release_candidate_v2_4.json')
      .pipe(map((release) => release.matches.map((prediction: any) => this.toReleaseCandidate(prediction))));
  }

  private getFromSnapshot(filename: string): Observable<MatchPrediction[]> {
    return this.http
      .get<BackendPrediction[]>(`assets/data/${filename}`)
      .pipe(map((predictions) => predictions.map((prediction) => this.toPrediction(prediction))));
  }

  private toPrediction(prediction: BackendPrediction): MatchPrediction {
    return {
      predictionId: prediction.prediction_id,
      matchId: prediction.match_id,
      generatedAt: prediction.generated_at,
      modelVersion: prediction.model_version,
      version: prediction.prediction_version,
      dataSourceType: prediction.data_source_type,
      isRealData: prediction.is_real_data,
      scoreMatrix: this.toScoreMatrix(prediction.score_matrix),
      markets: this.toMarkets(prediction.markets),
      confidence: prediction.confidence,
      topScores: prediction.top_scores.map((score) => this.toScoreProbability(score)),
    };
  }

  private toScoreMatrix(matrix: BackendScoreMatrix): ScoreMatrix {
    return {
      matchId: matrix.match_id,
      maxGoals: matrix.max_goals,
      probabilities: matrix.probabilities.map((score) => this.toScoreProbability(score)),
    };
  }

  private toScoreProbability(score: BackendScoreProbability): ScoreProbability {
    return {
      score: score.score,
      homeGoals: score.home_goals,
      awayGoals: score.away_goals,
      probability: score.probability,
    };
  }

  private toMarkets(markets: BackendMarkets): MatchMarkets {
    return {
      homeWin: markets.home_win,
      draw: markets.draw,
      awayWin: markets.away_win,
      homeOrDraw: markets.home_or_draw,
      awayOrDraw: markets.away_or_draw,
      noDraw: markets.no_draw,
      over05: markets.over_0_5,
      over15: markets.over_1_5,
      over25: markets.over_2_5,
      over35: markets.over_3_5,
      under25: markets.under_2_5,
      under35: markets.under_3_5,
      bttsYes: markets.btts_yes,
      bttsNo: markets.btts_no,
    };
  }

  private toReleaseCandidate(prediction: any): ReleaseCandidatePrediction {
    return {
      fixtureId: prediction.fixture_id,
      matchId: prediction.match_id,
      group: prediction.group,
      stage: prediction.stage,
      kickoffAt: prediction.kickoff_at,
      homeTeam: prediction.home_team,
      awayTeam: prediction.away_team,
      engineVersion: prediction.engine_version,
      releaseCandidateVersion: prediction.release_candidate_version,
      predictionVersion: prediction.prediction_version,
      generatedAt: prediction.generated_at,
      scoreMatrix: this.toScoreMatrix(prediction.score_matrix),
      topScores: prediction.top_scores.map((score: any) => {
        const [homeGoals, awayGoals] = score.score.split('-').map(Number);
        return { score: score.score, homeGoals, awayGoals, probability: score.probability };
      }),
      scoreModal: prediction.score_modal,
      probabilities: {
        homeWin: prediction.probabilities.home_win,
        draw: prediction.probabilities.draw,
        awayWin: prediction.probabilities.away_win,
      },
      markets: {
        doubleChance: {
          homeOrDraw: prediction.markets.double_chance.double_chance_1X,
          awayOrDraw: prediction.markets.double_chance.double_chance_X2,
          noDraw: prediction.markets.double_chance.double_chance_12,
        },
        drawNoBet: prediction.markets.draw_no_bet,
        overUnder: {
          over05: prediction.markets.over_under.over_0_5,
          over15: prediction.markets.over_under.over_1_5,
          over25: prediction.markets.over_under.over_2_5,
          over35: prediction.markets.over_under.over_3_5,
          under15: prediction.markets.over_under.under_1_5,
          under25: prediction.markets.over_under.under_2_5,
          under35: prediction.markets.over_under.under_3_5,
        },
        bothTeamsToScore: prediction.markets.both_teams_to_score,
        teamGoals: {
          homeOver05: prediction.markets.team_goals.team_home_over_0_5,
          awayOver05: prediction.markets.team_goals.team_away_over_0_5,
          homeOver15: prediction.markets.team_goals.team_home_over_1_5,
          awayOver15: prediction.markets.team_goals.team_away_over_1_5,
        },
      },
      confidence: {
        level: prediction.confidence.level,
        favoriteProbability: prediction.confidence.favorite_probability,
        outcomeGap: prediction.confidence.outcome_gap,
      },
      coherence: {
        favoriteScoreAligned: prediction.coherence.favorite_score_aligned,
        notes: prediction.coherence.notes,
      },
    };
  }
}
