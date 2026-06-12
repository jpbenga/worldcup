import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { GroupStrength, PredictionEvaluation, ReleaseCandidatePrediction, WorldCupGroup, WorldCupResult } from '../../models/worldcup.models';
import { GroupStandingsComponent } from '../group-standings/group-standings.component';
import { GroupStrengthSummaryComponent } from '../group-strength-summary/group-strength-summary.component';
import { TeamBadgeComponent } from '../team-badge/team-badge.component';

@Component({
  selector: 'app-group-tabs',
  imports: [DatePipe, PercentPipe, GroupStandingsComponent, GroupStrengthSummaryComponent, TeamBadgeComponent],
  templateUrl: './group-tabs.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupTabsComponent {
  @Input({ required: true }) groups: WorldCupGroup[] = [];
  @Input({ required: true }) strengths: GroupStrength[] = [];
  @Input({ required: true }) predictions: ReleaseCandidatePrediction[] = [];
  @Input({ required: true }) results: WorldCupResult[] = [];
  @Input({ required: true }) evaluations: PredictionEvaluation[] = [];
  @Output() matchSelected = new EventEmitter<string>();
  readonly selectedGroup = signal('A');

  get currentGroup(): WorldCupGroup | undefined {
    return this.groups.find((group) => group.group === this.selectedGroup()) ?? this.groups[0];
  }

  get matchCount(): number {
    return this.groups.reduce((total, group) => total + group.matches.length, 0);
  }

  strengthFor(group: string): GroupStrength | undefined {
    return this.strengths.find((strength) => strength.group === group);
  }

  predictionFor(matchId: string): ReleaseCandidatePrediction | undefined {
    return this.predictions.find((prediction) => prediction.matchId === matchId);
  }

  resultFor(matchId: string): WorldCupResult | undefined {
    return this.results.find((result) => result.matchId === matchId);
  }

  evaluationFor(matchId: string): PredictionEvaluation | undefined {
    return this.evaluations.find((evaluation) => evaluation.matchId === matchId);
  }
}
