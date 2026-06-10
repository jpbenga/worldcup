import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { GroupStanding } from '../../models/worldcup.models';

@Component({
  selector: 'app-group-standings',
  templateUrl: './group-standings.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupStandingsComponent {
  @Input({ required: true }) standings: GroupStanding[] = [];
}
