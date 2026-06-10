import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { WorldCupTeam } from '../../models/worldcup.models';

@Component({
  selector: 'app-team-badge',
  templateUrl: './team-badge.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TeamBadgeComponent {
  @Input({ required: true }) team!: WorldCupTeam;
  @Input() compact = false;
}
