export type DataSourceType = 'mock' | 'raw' | 'normalized' | 'generated' | 'evaluated' | 'manual' | 'api';

export interface DataSourceInfo {
  id: string;
  label: string;
  sourceType: DataSourceType;
  sourceName: string;
  isRealData: boolean;
  path: string;
  description: string;
}

export interface DataSourcesSnapshot {
  version: string;
  updatedAt: string;
  sources: DataSourceInfo[];
}

export interface AcquisitionSourceStatus {
  id: string;
  label: string;
  configured: boolean;
  reachable: boolean;
  usable: boolean;
  worldcup2026Found: boolean;
  notes: string;
}

export interface DataAcquisitionStatus {
  updatedAt: string;
  sources: AcquisitionSourceStatus[];
}

export interface TeamMappingStatus {
  updatedAt: string;
  status: 'PASS' | 'PASS_WITH_REVIEW_REQUIRED' | 'FAIL';
  apiFootballTotal: number;
  eloTotal: number;
  matched: number;
  autoValidated: number;
  needsReview: number;
  unmappedApiFootball: number;
  coveragePercent: number;
  eloConnectedToPredictionEngine: boolean;
}

export interface ModelComparisonDelta {
  homeWin: number;
  draw: number;
  awayWin: number;
  over25?: number;
  bttsYes?: number;
}

export interface ModelComparison {
  matchId: string;
  baselineModelVersion: string;
  eloModelVersion: string;
  homeTeam?: string;
  awayTeam?: string;
  eloAvailable: boolean;
  homeElo?: number;
  awayElo?: number;
  deltas: ModelComparisonDelta;
  baselineTopScore?: string;
  eloTopScore?: string;
  impactLevel: 'none' | 'low' | 'medium' | 'high';
}

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
  sourceType: DataSourceType;
  sourceName: string;
  isRealFixture: boolean;
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
  predictionId: string;
  matchId: string;
  generatedAt: string;
  modelVersion: string;
  version: string;
  dataSourceType: DataSourceType;
  isRealData: boolean;
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
  sourceType: DataSourceType;
  isRealData: boolean;
}
