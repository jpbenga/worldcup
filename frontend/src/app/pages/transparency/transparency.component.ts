import { AsyncPipe, DatePipe, KeyValuePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest, map } from 'rxjs';
import { WorldCupService } from '../../services/worldcup.service';

@Component({
  selector: 'app-transparency',
  imports: [AsyncPipe, DatePipe, KeyValuePipe, PercentPipe, RouterLink],
  templateUrl: './transparency.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TransparencyComponent {
  private readonly worldCupService = inject(WorldCupService);

  readonly transparency$ = combineLatest({
    history: this.worldCupService.getPredictionHistoryV212(),
    scoreboard: this.worldCupService.getModelScoreboardV212(),
    timeline: this.worldCupService.getPredictionTimelineV212(),
    copy: this.worldCupService.getPublicTransparencyCopyV212(),
  }).pipe(
    map((data) => ({
      ...data,
      evaluatedMatches: data.history.matches.filter((match: any) => match.evaluation.available),
    })),
  );

  rate(metric: any): number {
    return metric?.rate ?? 0;
  }
}
