import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import {
  GroupStanding,
  GroupStrength,
  Match,
  PredictionDiversityAudit,
  TournamentSimulation,
  TournamentTeamSimulation,
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
}
