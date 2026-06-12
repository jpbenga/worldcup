import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { GroupStanding, GroupStrength, MatchState, WorldCupGroup } from '../../models/worldcup.models';
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
}
