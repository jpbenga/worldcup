import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { GroupStrength } from '../../models/worldcup.models';

@Component({
  selector: 'app-group-strength-summary',
  imports: [DecimalPipe],
  templateUrl: './group-strength-summary.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupStrengthSummaryComponent {
  @Input() strength?: GroupStrength;
}
