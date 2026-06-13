import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { GroupStanding, GroupStrength, MatchState, WorldCupGroup } from '../../models/worldcup.models';
import { PredictionOutcomeState } from '../prediction-outcome-badge/prediction-outcome-badge.component';
import { GroupStandingsComponent } from '../group-standings/group-standings.component';
import { GroupStrengthSummaryComponent } from '../group-strength-summary/group-strength-summary.component';
import { TeamBadgeComponent } from '../team-badge/team-badge.component';

@Component({
  selector: 'app-group-tabs',
  imports: [DatePipe, GroupStandingsComponent, GroupStrengthSummaryComponent, TeamBadgeComponent],
  templateUrl: './group-tabs.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupTabsComponent {
  @Input({ required: true }) groups: WorldCupGroup[] = [];
  @Input({ required: true }) strengths: GroupStrength[] = [];
  @Input({ required: true }) matchStates: MatchState[] = [];
  @Input({ required: true }) liveStandings: Record<string, GroupStanding[]> = {};
  @Output() matchSelected = new EventEmitter<string>();
  readonly selectedGroup = signal('A');
  readonly selectedMatchday = signal(1);

  get currentGroup(): WorldCupGroup | undefined {
    return this.groups.find((group) => group.group === this.selectedGroup()) ?? this.groups[0];
  }

  get matchCount(): number {
    return this.groups.reduce((total, group) => total + group.matches.length, 0);
  }

  strengthFor(group: string): GroupStrength | undefined {
    return this.strengths.find((strength) => strength.group === group);
  }

  stateFor(matchId: string): MatchState | undefined {
    return this.matchStates.find((state) => state.matchId === matchId);
  }

  standingsFor(group: string): GroupStanding[] {
    return this.liveStandings[group] ?? [];
  }

  matchdayFor(round?: string): number {
    const match = round?.match(/(\d+)$/);
    return match ? Number(match[1]) : 1;
  }

  matchesForMatchday(group: WorldCupGroup): WorldCupGroup['matches'] {
    return group.matches.filter((match) => this.matchdayFor(match.round) === this.selectedMatchday());
  }

  selectGroup(group: string): void {
    this.selectedGroup.set(group);
    this.selectedMatchday.set(1);
  }

  changeMatchday(delta: number): void {
    this.selectedMatchday.set(Math.min(3, Math.max(1, this.selectedMatchday() + delta)));
  }

  outcomeState(state: MatchState): PredictionOutcomeState {
    if (state.status !== 'finished' || !state.evaluation.available) return 'pending';
    if (state.evaluation.exactScoreHit) return 'success';
    if (state.evaluation.oneXTwoHit || state.evaluation.top3Hit || state.evaluation.top5Hit) return 'partial';
    return 'fail';
  }

  cardClasses(state: MatchState): string {
    if (state.status === 'live') return 'border-amber-400/50 bg-amber-500/10 hover:border-amber-300';
    if (state.status !== 'finished') return 'border-cyan-500/25 bg-cyan-500/5 hover:border-cyan-400/50';
    return {
      success: 'border-emerald-500/45 bg-emerald-500/10 hover:border-emerald-300',
      partial: 'border-cyan-500/45 bg-cyan-500/10 hover:border-cyan-300',
      fail: 'border-rose-500/45 bg-rose-500/10 hover:border-rose-300',
      push: 'border-amber-500/45 bg-amber-500/10 hover:border-amber-300',
      pending: 'border-slate-700 bg-slate-900/70 hover:border-slate-500',
      neutral: 'border-slate-700 bg-slate-900/70 hover:border-slate-500',
    }[this.outcomeState(state)];
  }

  statusLabel(state: MatchState): string {
    return state.status === 'finished' ? 'Terminé' : state.status === 'live' ? 'En direct' : 'À venir';
  }

  evaluationLabel(state: MatchState): string {
    if (state.evaluation.exactScoreHit) return 'Score exact';
    if (state.evaluation.oneXTwoHit) return 'Bon résultat, score différent';
    if (state.evaluation.top3Hit || state.evaluation.top5Hit) return 'Score dans la sélection';
    return 'Prono raté';
  }
}
