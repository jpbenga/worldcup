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
