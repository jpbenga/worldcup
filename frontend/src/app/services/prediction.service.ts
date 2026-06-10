import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import {
  MatchMarkets,
  MatchPrediction,
  DataSourceType,
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
}
