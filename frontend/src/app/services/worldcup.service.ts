import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import {
  ActiveCandidateSimulationComparison,
  DualMatrixComparison,
  GroupStanding,
  GroupStrength,
  ConditionedTournamentSimulation,
  CreativeTournamentExperience,
  LiveGroupStandings,
  Match,
  MatchState,
  PredictionEvaluation,
  PredictionDiversityAudit,
  ProjectedCampaign,
  SimulationTeamDelta,
  TournamentSimulation,
  TournamentTeamSimulation,
  WorldCupResult,
  WorldCupGroup,
  WorldCupTeam,
} from '../models/worldcup.models';

@Injectable({ providedIn: 'root' })
export class WorldCupService {
  private readonly http = inject(HttpClient);

  getGroups(): Observable<WorldCupGroup[]> {
    return this.http.get<any[]>('assets/data/worldcup_groups.json').pipe(
      map((groups) =>
        groups.map((group) => ({
          group: group.group,
          groupLabel: group.group_label,
          teams: group.teams.map((team: any) => this.team(team)),
          matches: group.matches.map((match: any) => this.match(match)),
          standingsAvailable: group.standings_available,
          standings: group.standings.map((row: any) => this.standing(row)),
        })),
      ),
    );
  }

  getStrengths(): Observable<GroupStrength[]> {
    return this.http.get<any[]>('assets/data/group_strengths.json').pipe(
      map((items) =>
        items.map((item) => ({
          group: item.group,
          groupLabel: item.group_label,
          groupDataAvailable: item.group_data_available,
          teamCount: item.team_count,
          matchCount: item.match_count,
          averageElo: item.average_elo,
          maxElo: item.max_elo,
          minElo: item.min_elo,
          strongestTeam: item.strongest_team,
          weakestTeam: item.weakest_team,
        })),
      ),
    );
  }

  getDiversityAudit(): Observable<PredictionDiversityAudit> {
    return this.http.get<any>('assets/data/prediction_diversity_audit.json').pipe(
      map((audit) => ({
        totalMatches: audit.total_matches,
        baselineTopScoreDistribution: audit.baseline_top_score_distribution,
        eloTopScoreDistribution: audit.elo_top_score_distribution,
        oneOneRateBaseline: audit.one_one_rate_baseline,
        oneOneRateElo: audit.one_one_rate_elo,
        topScoreChangedCount: audit.top_score_changed_count,
        maxDelta: audit.max_delta,
        isHighlyUniform: audit.is_highly_uniform,
        engineWarning: audit.engine_warning,
      })),
    );
  }

  getTournamentSimulation(): Observable<TournamentSimulation> {
    return this.http.get<any>('assets/data/worldcup_tournament_simulation_v2_4.json').pipe(
      map((simulation) => {
        const teams = Object.entries(simulation.teams).map(([team, item]) =>
          this.tournamentTeam(team, item as any),
        );
        return {
          generatedAt: simulation.generated_at,
          version: simulation.version,
          engineVersion: simulation.engine_version,
          simulationCount: simulation.simulation_count,
          fixtureCount: simulation.fixture_count,
          fullTournamentSimulationAvailable: simulation.full_tournament_simulation_available,
          groupStageSimulationAvailable: simulation.group_stage_simulation_available,
          qualificationRule: simulation.qualification_rule,
          limitations: simulation.limitations,
          teams,
          groups: Object.entries(simulation.groups).map(([group, groupTeams]) => ({
            group,
            teams: (groupTeams as string[]).map((team) => teams.find((item) => item.team === team)!),
          })),
        };
      }),
    );
  }

  getResults(): Observable<WorldCupResult[]> {
    return this.http.get<any>('assets/data/worldcup_2026_results_v2_6.json').pipe(
      map((payload) => payload.fixtures.map((item: any) => ({
        fixtureId: item.fixture_id,
        matchId: item.match_id,
        homeTeam: item.home_team,
        awayTeam: item.away_team,
        kickoffAt: item.kickoff_at,
        status: item.status,
        elapsed: item.elapsed,
        actualScore: { home: item.actual_score.home, away: item.actual_score.away },
        winner: item.winner,
        confidence: item.confidence,
      }))),
    );
  }

  getMatchStates(): Observable<MatchState[]> {
    return this.http.get<any>('assets/data/worldcup_match_state_view_model_v2_7.json').pipe(
      map((payload) => payload.matches.map((item: any) => this.matchState(item))),
    );
  }

  getLiveGroupStandings(): Observable<LiveGroupStandings> {
    return this.http.get<any>('assets/data/worldcup_live_group_standings_v2_7.json').pipe(
      map((payload) => ({
        finishedMatchesCount: payload.finished_matches_count,
        groups: Object.fromEntries(Object.entries(payload.groups).map(([group, item]: [string, any]) => [
          group,
          item.standings.map((row: any) => ({
            rank: row.rank,
            teamId: 0,
            teamName: row.team,
            points: row.points,
            played: row.played,
            won: row.wins,
            drawn: row.draws,
            lost: row.losses,
            goalsFor: row.goals_for,
            goalsAgainst: row.goals_against,
            goalDifference: row.goal_difference,
          })),
        ])),
      })),
    );
  }

  getPredictionEvaluations(): Observable<PredictionEvaluation[]> {
    return this.http.get<any>('assets/data/worldcup_2026_prediction_evaluation_v2_6.json').pipe(
      map((payload) => payload.matches.map((item: any) => ({
        matchId: item.match_id,
        actualScore: item.actual_score,
        scoreModal: item.score_modal,
        exactScoreHit: item.exact_score_hit,
        top3ScoreHit: item.top_3_score_hit,
        top5ScoreHit: item.top_5_score_hit,
        predicted1x2: item.predicted_1x2,
        actual1x2: item.actual_1x2,
        oneXTwoHit: item.one_x_two_hit,
        drawNoBet: item.draw_no_bet,
        overUnder: item.over_under,
        bttsHit: item.btts_hit,
        teamGoalsHit: item.team_goals_hit,
        predictionEvaluationLabel: item.prediction_evaluation_label,
        postMatchSummary: item.post_match_summary,
      }))),
    );
  }

  getConditionedTournamentSimulation(): Observable<ConditionedTournamentSimulation> {
    return this.http.get<any>('assets/data/worldcup_tournament_simulation_conditioned_v2_6.json').pipe(
      map((simulation) => {
        const base = this.tournamentSimulation(simulation);
        return {
          ...base,
          finishedMatchesLocked: simulation.finished_matches_locked,
          futureMatchesSimulated: simulation.future_matches_simulated,
          changesVsV24: simulation.changes_vs_v2_4,
          largestRises: simulation.largest_rises,
          largestFalls: simulation.largest_falls,
        };
      }),
    );
  }

  getProjectedCampaign(): Observable<ProjectedCampaign> {
    return this.http.get<any>('assets/data/worldcup_projected_campaign_v2_6.json').pipe(
      map((campaign) => ({
        pathType: campaign.path_type,
        isOfficialChampionSimulation: campaign.is_official_champion_simulation,
        championProxy: campaign.champion_proxy,
        championProxyScore: campaign.champion_proxy_score,
        topContenders: campaign.top_contenders.map((item: any) => ({
          team: item.team,
          group: item.group,
          qualificationProbability: item.qualification_probability,
          groupWinnerProbability: item.group_winner_probability,
          eloRating: item.elo_rating,
          eloRank: item.elo_rank,
          contenderProxyScore: item.contender_proxy_score,
          mostProbableGroupFinish: item.most_probable_group_finish,
          campaignSteps: item.campaign_steps,
        })),
        limitations: campaign.limitations,
      })),
    );
  }

  getDualMatrixComparisons(): Observable<DualMatrixComparison[]> {
    return this.http.get<any>('assets/data/dual_matrix_comparison_v2_9.json').pipe(
      map((payload) => payload.matches.map((item: any) => ({
        matchId: item.match_id,
        homeTeam: item.home_team,
        awayTeam: item.away_team,
        favorite: item.favorite,
        favoriteProbability: item.favorite_probability,
        active: this.dualProjection(item.active),
        candidate: this.dualProjection(item.candidate),
        comparison: {
          modalChanged: item.comparison.modal_changed,
          modalChange: item.comparison.modal_change,
          totalXgDelta: item.comparison.total_xg_delta,
          favoriteMarginDelta: item.comparison.favorite_margin_delta,
          over25Delta: item.comparison.over_2_5_delta,
          label: item.comparison.label,
        },
      }))),
    );
  }

  getCandidateTournamentSimulation(): Observable<ConditionedTournamentSimulation> {
    return this.http.get<any>('assets/data/worldcup_tournament_simulation_candidate_v2_9.json').pipe(
      map((simulation) => ({
        ...this.tournamentSimulation(simulation),
        finishedMatchesLocked: simulation.finished_matches_locked,
        futureMatchesSimulated: simulation.future_matches_simulated,
        changesVsV24: {},
        largestRises: [],
        largestFalls: [],
      })),
    );
  }

  getCandidateProjectedCampaign(): Observable<ProjectedCampaign> {
    return this.http.get<any>('assets/data/worldcup_projected_campaign_candidate_v2_9.json').pipe(
      map((campaign) => this.projectedCampaign(campaign)),
    );
  }

  getActiveCandidateSimulationComparison(): Observable<ActiveCandidateSimulationComparison> {
    return this.http.get<any>('assets/data/active_vs_candidate_simulation_comparison_v2_9.json').pipe(
      map((payload) => ({
        teamsRisingMost: payload.teams_rising_most.map((item: any) => this.simulationDelta(item)),
        teamsFallingMost: payload.teams_falling_most.map((item: any) => this.simulationDelta(item)),
        groupsMostAffected: payload.groups_most_affected.map((item: any) => ({
          group: item.group,
          averageAbsoluteQualificationDelta: item.average_absolute_qualification_delta,
          maximumAbsoluteQualificationDelta: item.maximum_absolute_qualification_delta,
        })),
        diagnosis: {
          maximumAbsoluteQualificationDelta: payload.diagnosis.maximum_absolute_qualification_delta,
          changesQualificationsStrongly: payload.diagnosis.changes_qualifications_strongly,
          changesScoresMoreThanQualifications: payload.diagnosis.changes_scores_more_than_qualifications,
        },
      })),
    );
  }

  getCreativeTournamentExperience(): Observable<CreativeTournamentExperience> {
    return this.http.get<any>('assets/data/creative_tournament_experience_v2_11.json').pipe(
      map((payload) => ({
        version: payload.version,
        engineVersion: payload.engine_version,
        candidateVersion: payload.candidate_version,
        generatedAt: payload.generated_at,
        refresh: {
          sourceManifest: payload.refresh.source_manifest,
          simulationCount: payload.refresh.simulation_count,
          finishedMatches: payload.refresh.finished_matches,
          liveMatches: payload.refresh.live_matches,
          notStartedMatches: payload.refresh.not_started_matches,
        },
        tournamentLeader: {
          team: payload.tournament_leader.team,
          label: payload.tournament_leader.label,
          activeProxyRank: payload.tournament_leader.active_proxy_rank,
          candidateProxyRank: payload.tournament_leader.candidate_proxy_rank,
          activeQualificationProbability: payload.tournament_leader.active_qualification_probability,
          candidateQualificationProbability: payload.tournament_leader.candidate_qualification_probability,
          activeGroupWinnerProbability: payload.tournament_leader.active_group_winner_probability,
          candidateGroupWinnerProbability: payload.tournament_leader.candidate_group_winner_probability,
          confidenceLabel: payload.tournament_leader.confidence_label,
          isOfficialChampionSimulation: payload.tournament_leader.is_official_champion_simulation,
          explanation: payload.tournament_leader.explanation,
        },
        topContenders: payload.top_contenders.map((item: any) => ({
          rank: item.rank,
          team: item.team,
          group: item.group,
          activeScore: item.active_score,
          candidateScore: item.candidate_score,
          qualificationProbability: item.qualification_probability,
          candidateQualificationProbability: item.candidate_qualification_probability,
          groupWinnerProbability: item.group_winner_probability,
          activeVsCandidateDelta: item.active_vs_candidate_delta,
          status: item.status,
          reason: item.reason,
        })),
        projectedCampaign: {
          bracketAvailable: payload.projected_campaign.bracket_available,
          isOfficialChampionSimulation: payload.projected_campaign.is_official_champion_simulation,
          leader: payload.projected_campaign.leader,
          groupExitProbability: payload.projected_campaign.group_exit_probability,
          groupWinnerProbability: payload.projected_campaign.group_winner_probability,
          contenderStatus: payload.projected_campaign.contender_status,
          estimatedAdversity: payload.projected_campaign.estimated_adversity,
          steps: payload.projected_campaign.steps,
          proxyLimit: payload.projected_campaign.proxy_limit,
        },
        activeVsAlternative: {
          summary: payload.active_vs_alternative.summary,
          activeLeader: payload.active_vs_alternative.active_leader,
          alternativeLeader: payload.active_vs_alternative.alternative_leader,
          modalScoresChanged: payload.active_vs_alternative.modal_scores_changed,
          favoriteMarginsIncreased: payload.active_vs_alternative.favorite_margins_increased,
          mostAffectedGroups: payload.active_vs_alternative.most_affected_groups,
          teamsRising: payload.active_vs_alternative.teams_rising,
          teamsFalling: payload.active_vs_alternative.teams_falling,
          leaderChanged: payload.active_vs_alternative.leader_changed,
          interpretation: payload.active_vs_alternative.interpretation,
        },
        groupStorylines: payload.group_storylines.map((item: any) => ({
          group: item.group,
          title: item.title,
          summary: item.summary,
          mostLikelyWinner: item.most_likely_winner,
          qualificationFavorites: item.qualification_favorites,
          mostOpenRank: item.most_open_rank,
          chaosScore: item.chaos_score,
          activeCandidateDifference: item.active_candidate_difference,
          lockedResults: item.locked_results,
          storyType: item.story_type,
          label: item.label,
        })),
        openGroups: payload.open_groups.map((item: any) => ({
          group: item.group,
          title: item.title,
          chaosScore: item.chaos_score,
          label: item.label,
        })),
        lockedResultImpact: payload.locked_result_impact.map((item: any) => ({
          match: item.match,
          group: item.group,
          winner: item.winner,
          qualificationDelta: item.qualification_delta,
          summary: item.summary,
        })),
        limitations: payload.limitations,
      })),
    );
  }

  private team(team: any): WorldCupTeam {
    return {
      teamId: team.team_id,
      apiFootballTeamId: team.api_football_team_id,
      name: team.name,
      country: team.country,
      countryCode: team.country_code,
      logoUrl: team.logo_url,
      flagUrl: team.flag_url,
      eloRating: team.elo_rating,
      eloRank: team.elo_rank,
    };
  }

  private match(match: any): Match {
    return {
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
      round: match.round,
      venue: match.venue,
      city: match.city,
      homeTeamLogoUrl: match.home_team_logo_url,
      awayTeamLogoUrl: match.away_team_logo_url,
    };
  }

  private standing(row: any): GroupStanding {
    return {
      rank: row.rank,
      teamId: row.team_id,
      teamName: row.team_name,
      logoUrl: row.logo_url,
      points: row.points,
      played: row.played,
      won: row.won,
      drawn: row.drawn,
      lost: row.lost,
      goalsFor: row.goals_for,
      goalsAgainst: row.goals_against,
      goalDifference: row.goal_difference,
    };
  }

  private tournamentTeam(team: string, item: any): TournamentTeamSimulation {
    return {
      team,
      group: item.group,
      finishFirstProbability: item.finish_first_probability,
      finishSecondProbability: item.finish_second_probability,
      finishThirdProbability: item.finish_third_probability,
      finishFourthProbability: item.finish_fourth_probability,
      qualificationProbability: item.qualification_probability,
      bestThirdQualificationProbability: item.best_third_qualification_probability,
      groupEliminationProbability: item.group_elimination_probability,
    };
  }

  private tournamentSimulation(simulation: any): TournamentSimulation {
    const teams = Object.entries(simulation.teams).map(([team, item]) => this.tournamentTeam(team, item as any));
    return {
      generatedAt: simulation.generated_at,
      version: simulation.version,
      engineVersion: simulation.engine_version,
      simulationCount: simulation.simulation_count,
      fixtureCount: simulation.fixture_count,
      fullTournamentSimulationAvailable: simulation.full_tournament_simulation_available,
      groupStageSimulationAvailable: simulation.group_stage_simulation_available,
      qualificationRule: simulation.qualification_rule,
      limitations: simulation.limitations,
      teams,
      groups: Object.entries(simulation.groups).map(([group, groupTeams]) => ({
        group,
        teams: (groupTeams as string[]).map((team) => teams.find((item) => item.team === team)!),
      })),
    };
  }

  private projectedCampaign(campaign: any): ProjectedCampaign {
    return {
      pathType: campaign.path_type,
      isOfficialChampionSimulation: campaign.is_official_champion_simulation,
      championProxy: campaign.champion_proxy,
      championProxyScore: campaign.champion_proxy_score,
      topContenders: campaign.top_contenders.map((item: any) => ({
        team: item.team,
        group: item.group,
        qualificationProbability: item.qualification_probability,
        groupWinnerProbability: item.group_winner_probability,
        eloRating: item.elo_rating,
        eloRank: item.elo_rank,
        contenderProxyScore: item.contender_proxy_score,
        mostProbableGroupFinish: item.most_probable_group_finish,
        campaignSteps: item.campaign_steps,
      })),
      limitations: campaign.limitations,
    };
  }

  private dualProjection(item: any) {
    return {
      scoreModal: item.score_modal,
      scoreModalProbability: item.score_modal_probability,
      topScores: item.top_scores,
      expectedGoals: item.expected_goals,
      markets: {
        over15: item.markets.over_1_5,
        over25: item.markets.over_2_5,
        bttsYes: item.markets.btts_yes,
        homeScores2Plus: item.markets.home_scores_2_plus,
        awayScores2Plus: item.markets.away_scores_2_plus,
        favoriteWinBy2Plus: item.markets.favorite_win_by_2_plus,
      },
    };
  }

  private simulationDelta(item: any): SimulationTeamDelta {
    return {
      team: item.team,
      group: item.group,
      qualificationDelta: item.qualification_delta,
      groupWinnerDelta: item.group_winner_delta,
      groupSecondDelta: item.group_second_delta,
      groupThirdDelta: item.group_third_delta,
    };
  }

  private matchState(item: any): MatchState {
    const probabilities = item.prediction.probabilities_1x2;
    const matrix = item.prediction.score_matrix;
    return {
      fixtureId: item.fixture_id,
      matchId: item.match_id,
      group: item.group,
      matchdayLabel: item.matchday_label,
      homeTeam: item.home_team,
      awayTeam: item.away_team,
      kickoffAt: item.kickoff_at,
      venue: item.venue,
      city: item.city,
      homeTeamLogoUrl: item.home_team_logo_url,
      awayTeamLogoUrl: item.away_team_logo_url,
      status: item.status,
      result: {
        available: item.result.available,
        homeGoals: item.result.home_goals,
        awayGoals: item.result.away_goals,
        winner: item.result.winner,
        source: item.result.source,
      },
      prediction: {
        engineVersion: item.prediction.engine_version,
        scoreModal: item.prediction.score_modal,
        scoreModalProbability: item.prediction.score_modal_probability,
        topScores: item.prediction.top_scores.map((score: any) => {
          const [homeGoals, awayGoals] = score.score.split('-').map(Number);
          return { score: score.score, probability: score.probability, homeGoals, awayGoals };
        }),
        scoreMatrix: {
          matchId: matrix.match_id,
          maxGoals: matrix.max_goals,
          probabilities: matrix.probabilities.map((score: any) => ({
            score: score.score, probability: score.probability, homeGoals: score.home_goals, awayGoals: score.away_goals,
          })),
        },
        probabilities1x2: { homeWin: probabilities.home_win, draw: probabilities.draw, awayWin: probabilities.away_win },
        favorite1x2: item.prediction.favorite_1x2,
        favoriteLabel: item.prediction.favorite_label,
        favoriteProbability: item.prediction.favorite_probability,
        scoreConsistentWithFavorite: item.prediction.score_consistent_with_favorite,
        scoreConsistentWithFavoriteProbability: item.prediction.score_consistent_with_favorite_probability,
        coherenceStatus: item.prediction.coherence_status,
        coherenceExplanation: item.prediction.coherence_explanation,
        confidence: {
          level: item.prediction.confidence.level,
          favoriteProbability: item.prediction.confidence.favorite_probability,
          outcomeGap: item.prediction.confidence.outcome_gap,
        },
        markets: {
          doubleChance: {
            homeOrDraw: item.prediction.markets.double_chance.double_chance_1X,
            awayOrDraw: item.prediction.markets.double_chance.double_chance_X2,
            noDraw: item.prediction.markets.double_chance.double_chance_12,
          },
          drawNoBet: item.prediction.markets.draw_no_bet,
          overUnder: {
            over05: item.prediction.markets.over_under.over_0_5,
            over15: item.prediction.markets.over_under.over_1_5,
            over25: item.prediction.markets.over_under.over_2_5,
            over35: item.prediction.markets.over_under.over_3_5,
            under15: item.prediction.markets.over_under.under_1_5,
            under25: item.prediction.markets.over_under.under_2_5,
            under35: item.prediction.markets.over_under.under_3_5,
          },
          bothTeamsToScore: item.prediction.markets.both_teams_to_score,
          teamGoals: {
            homeOver05: item.prediction.markets.team_goals.team_home_over_0_5,
            awayOver05: item.prediction.markets.team_goals.team_away_over_0_5,
            homeOver15: item.prediction.markets.team_goals.team_home_over_1_5,
            awayOver15: item.prediction.markets.team_goals.team_away_over_1_5,
          },
        },
      },
      evaluation: {
        available: item.evaluation.available,
        summaryLabel: item.evaluation.summary_label,
        exactScoreHit: item.evaluation.exact_score_hit,
        top3Hit: item.evaluation.top_3_hit,
        top5Hit: item.evaluation.top_5_hit,
        oneXTwoHit: item.evaluation.one_x_two_hit,
        dnbOutcome: item.evaluation.dnb_outcome,
        marketHits: {
          overUnder: item.evaluation.market_hits.over_under,
          btts: item.evaluation.market_hits.btts,
          teamGoals: item.evaluation.market_hits.team_goals,
        },
      },
      display: {
        cardPrimaryScore: item.display.card_primary_score,
        cardSecondaryLabel: item.display.card_secondary_label,
        modalStatusLabel: item.display.modal_status_label,
        resultVsPredictionLabel: item.display.result_vs_prediction_label,
        showResultBlock: item.display.show_result_block,
        showCoherenceWarning: item.display.show_coherence_warning,
      },
    };
  }
}
