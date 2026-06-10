import { PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { PredictionDiversityAudit } from '../../models/worldcup.models';

@Component({
  selector: 'app-prediction-engine-warning',
  imports: [PercentPipe],
  templateUrl: './prediction-engine-warning.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PredictionEngineWarningComponent {
  @Input({ required: true }) audit!: PredictionDiversityAudit;
}
