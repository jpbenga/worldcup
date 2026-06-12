export type DataSourceType = 'mock' | 'raw' | 'normalized' | 'generated' | 'evaluated' | 'manual' | 'api' | 'api_football';

export interface PredictionEngineStatus {
  name: string;
  version: string;
  status: 'experimental';
  historicallyCalibrated: boolean;
  description: string;
}

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
  activeSource: string;
  isRealData: boolean;
  isFutureFixtureSet: boolean;
  backtestingStatus: string;
  engine: PredictionEngineStatus;
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
  isFutureFixture?: boolean;
  round?: string;
  venue?: string;
  city?: string;
  homeTeamLogoUrl?: string;
  awayTeamLogoUrl?: string;
}

export interface WorldCupTeam {
  teamId: string;
  apiFootballTeamId: number;
  name: string;
  country: string;
  countryCode: string;
  logoUrl?: string;
  flagUrl?: string;
  eloRating?: number;
  eloRank?: number;
}

export interface GroupStanding {
  rank: number;
  teamId: number;
  teamName: string;
  logoUrl?: string;
  points: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
}

export interface WorldCupGroup {
  group: string;
  groupLabel: string;
  teams: WorldCupTeam[];
  matches: Match[];
  standingsAvailable: boolean;
  standings: GroupStanding[];
}

export interface GroupStrength {
  group: string;
  groupLabel: string;
  groupDataAvailable: boolean;
  teamCount: number;
  matchCount: number;
  averageElo?: number;
  maxElo?: number;
  minElo?: number;
  strongestTeam?: string;
  weakestTeam?: string;
}

export interface PredictionDiversityAudit {
  totalMatches: number;
  baselineTopScoreDistribution: Record<string, number>;
  eloTopScoreDistribution: Record<string, number>;
  oneOneRateBaseline: number;
  oneOneRateElo: number;
  topScoreChangedCount: number;
  maxDelta: number;
  isHighlyUniform: boolean;
  engineWarning: string;
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

export interface ReleaseCandidateMarkets {
  doubleChance: {
    homeOrDraw: number;
    awayOrDraw: number;
    noDraw: number;
  };
  drawNoBet: {
    home: number;
    away: number;
  };
  overUnder: {
    over05: number;
    over15: number;
    over25: number;
    over35: number;
    under15: number;
    under25: number;
    under35: number;
  };
  bothTeamsToScore: {
    yes: number;
    no: number;
  };
  teamGoals: {
    homeOver05: number;
    awayOver05: number;
    homeOver15: number;
    awayOver15: number;
  };
}

export interface ReleaseCandidatePrediction {
  fixtureId: number;
  matchId: string;
  group: string;
  stage: string;
  kickoffAt: string;
  homeTeam: string;
  awayTeam: string;
  engineVersion: string;
  releaseCandidateVersion: string;
  predictionVersion: string;
  generatedAt: string;
  scoreMatrix: ScoreMatrix;
  topScores: ScoreProbability[];
  scoreModal: string;
  probabilities: {
    homeWin: number;
    draw: number;
    awayWin: number;
  };
  markets: ReleaseCandidateMarkets;
  confidence: {
    level: 'low' | 'medium' | 'high';
    favoriteProbability: number;
    outcomeGap: number;
  };
  coherence: {
    favoriteScoreAligned: boolean;
    notes: string[];
  };
}

export interface TournamentTeamSimulation {
  team: string;
  group: string;
  finishFirstProbability: number;
  finishSecondProbability: number;
  finishThirdProbability: number;
  finishFourthProbability: number;
  qualificationProbability: number;
  bestThirdQualificationProbability: number;
  groupEliminationProbability: number;
}

export interface TournamentGroupSimulation {
  group: string;
  teams: TournamentTeamSimulation[];
}

export interface TournamentSimulation {
  generatedAt: string;
  version: string;
  engineVersion: string;
  simulationCount: number;
  fixtureCount: number;
  fullTournamentSimulationAvailable: boolean;
  groupStageSimulationAvailable: boolean;
  qualificationRule: string;
  limitations: string[];
  teams: TournamentTeamSimulation[];
  groups: TournamentGroupSimulation[];
}

export type ResultStatus = 'not_started' | 'live' | 'finished' | 'postponed' | 'cancelled' | 'unknown';

export interface WorldCupResult {
  fixtureId: number;
  matchId: string;
  homeTeam: string;
  awayTeam: string;
  kickoffAt: string;
  status: ResultStatus;
  elapsed?: number;
  actualScore: { home?: number; away?: number };
  winner?: 'home' | 'draw' | 'away';
  confidence: 'official' | 'cached' | 'manual' | 'unknown';
}

export interface PredictionEvaluation {
  matchId: string;
  actualScore: string;
  scoreModal: string;
  exactScoreHit: boolean;
  top3ScoreHit: boolean;
  top5ScoreHit: boolean;
  predicted1x2: string;
  actual1x2: string;
  oneXTwoHit: boolean;
  drawNoBet: { selection: string; outcome: 'win' | 'loss' | 'push' | 'not_applicable' };
  overUnder: Record<string, boolean>;
  bttsHit: boolean;
  teamGoalsHit: Record<string, boolean>;
  predictionEvaluationLabel: string;
  postMatchSummary: string;
}

export interface ConditionedTournamentSimulation extends TournamentSimulation {
  finishedMatchesLocked: number;
  futureMatchesSimulated: number;
  changesVsV24: Record<string, number>;
  largestRises: [string, number][];
  largestFalls: [string, number][];
}

export interface ProjectedContender {
  team: string;
  group: string;
  qualificationProbability: number;
  groupWinnerProbability: number;
  eloRating?: number;
  eloRank?: number;
  contenderProxyScore: number;
  mostProbableGroupFinish: number;
  campaignSteps: { label: string; detail: string }[];
}

export interface ProjectedCampaign {
  pathType: 'projected_campaign_proxy';
  isOfficialChampionSimulation: boolean;
  championProxy: string;
  championProxyScore: number;
  topContenders: ProjectedContender[];
  limitations: string[];
}

export interface MatchStatePrediction {
  engineVersion: string;
  scoreModal: string;
  scoreModalProbability: number;
  topScores: ScoreProbability[];
  scoreMatrix: ScoreMatrix;
  probabilities1x2: { homeWin: number; draw: number; awayWin: number };
  favorite1x2: 'home' | 'draw' | 'away';
  favoriteLabel: string;
  favoriteProbability: number;
  scoreConsistentWithFavorite: string;
  scoreConsistentWithFavoriteProbability: number;
  coherenceStatus: 'modal_differs_from_1x2_favorite' | 'modal_aligned_with_1x2_favorite';
  coherenceExplanation: string;
  confidence: ReleaseCandidatePrediction['confidence'];
  markets: ReleaseCandidateMarkets;
}

export interface MatchState {
  fixtureId: number;
  matchId: string;
  group: string;
  matchdayLabel: string;
  homeTeam: string;
  awayTeam: string;
  kickoffAt: string;
  venue?: string;
  city?: string;
  homeTeamLogoUrl?: string;
  awayTeamLogoUrl?: string;
  status: ResultStatus;
  result: { available: boolean; homeGoals?: number; awayGoals?: number; winner?: string; source: string };
  prediction: MatchStatePrediction;
  evaluation: {
    available: boolean;
    summaryLabel: string;
    exactScoreHit?: boolean;
    top3Hit?: boolean;
    top5Hit?: boolean;
    oneXTwoHit?: boolean;
    dnbOutcome?: string;
    marketHits: { overUnder?: Record<string, boolean>; btts?: boolean; teamGoals?: Record<string, boolean> };
  };
  display: {
    cardPrimaryScore: string;
    cardSecondaryLabel: string;
    modalStatusLabel: string;
    resultVsPredictionLabel: string;
    showResultBlock: boolean;
    showCoherenceWarning: boolean;
  };
}

export interface LiveGroupStandings {
  finishedMatchesCount: number;
  groups: Record<string, GroupStanding[]>;
}

export interface DualMatrixProjection {
  scoreModal: string;
  scoreModalProbability: number;
  topScores: { score: string; probability: number }[];
  expectedGoals: { home: number; away: number; total: number };
  markets: {
    over15: number;
    over25: number;
    bttsYes: number;
    homeScores2Plus: number;
    awayScores2Plus: number;
    favoriteWinBy2Plus: number;
  };
}

export interface DualMatrixComparison {
  matchId: string;
  homeTeam: string;
  awayTeam: string;
  favorite: string;
  favoriteProbability: number;
  active: DualMatrixProjection;
  candidate: DualMatrixProjection;
  comparison: {
    modalChanged: boolean;
    modalChange: string;
    totalXgDelta: number;
    favoriteMarginDelta: number;
    over25Delta: number;
    label: string;
  };
}

export interface SimulationTeamDelta {
  team: string;
  group: string;
  qualificationDelta: number;
  groupWinnerDelta: number;
  groupSecondDelta: number;
  groupThirdDelta: number;
}

export interface ActiveCandidateSimulationComparison {
  teamsRisingMost: SimulationTeamDelta[];
  teamsFallingMost: SimulationTeamDelta[];
  groupsMostAffected: { group: string; averageAbsoluteQualificationDelta: number; maximumAbsoluteQualificationDelta: number }[];
  diagnosis: {
    maximumAbsoluteQualificationDelta: number;
    changesQualificationsStrongly: boolean;
    changesScoresMoreThanQualifications: boolean;
  };
}

export interface CreativeTournamentContender {
  rank: number;
  team: string;
  group: string;
  activeScore?: number;
  candidateScore?: number;
  qualificationProbability: number;
  candidateQualificationProbability: number;
  groupWinnerProbability: number;
  activeVsCandidateDelta: number;
  status: 'stable' | 'rising' | 'falling' | 'volatile';
  reason: string;
}

export interface CreativeGroupStoryline {
  group: string;
  title: string;
  summary: string;
  mostLikelyWinner: string;
  qualificationFavorites: string[];
  mostOpenRank: string;
  chaosScore: number;
  activeCandidateDifference: string;
  lockedResults: { match: string; summary: string }[];
  storyType: 'favorite_control' | 'open_group' | 'upset_watch' | 'volatile' | 'low_change';
  label: string;
}

export interface CreativeTournamentExperience {
  version: string;
  engineVersion: string;
  candidateVersion: string;
  generatedAt: string;
  refresh: {
    sourceManifest: string;
    simulationCount: number;
    finishedMatches: number;
    liveMatches: number;
    notStartedMatches: number;
  };
  tournamentLeader: {
    team: string;
    label: string;
    activeProxyRank: number;
    candidateProxyRank: number;
    activeQualificationProbability: number;
    candidateQualificationProbability: number;
    activeGroupWinnerProbability: number;
    candidateGroupWinnerProbability: number;
    confidenceLabel: 'stable' | 'contested' | 'open';
    isOfficialChampionSimulation: boolean;
    explanation: string;
  };
  topContenders: CreativeTournamentContender[];
  projectedCampaign: {
    bracketAvailable: boolean;
    isOfficialChampionSimulation: boolean;
    leader: string;
    groupExitProbability: number;
    groupWinnerProbability: number;
    contenderStatus: string;
    estimatedAdversity: string;
    steps: { label: string; detail: string }[];
    proxyLimit: string;
  };
  activeVsAlternative: {
    summary: string;
    activeLeader: string;
    alternativeLeader: string;
    modalScoresChanged: number;
    favoriteMarginsIncreased: number;
    mostAffectedGroups: string[];
    teamsRising: string[];
    teamsFalling: string[];
    leaderChanged: boolean;
    interpretation: string;
  };
  groupStorylines: CreativeGroupStoryline[];
  openGroups: { group: string; title: string; chaosScore: number; label: string }[];
  lockedResultImpact: {
    match: string;
    group: string;
    winner: string;
    qualificationDelta: Record<string, string>;
    summary: string;
  }[];
  limitations: string[];
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
