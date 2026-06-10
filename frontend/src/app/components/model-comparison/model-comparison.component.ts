import { DecimalPipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ModelComparison } from '../../models/worldcup.models';

@Component({
  selector: 'app-model-comparison',
  imports: [DecimalPipe, PercentPipe],
  templateUrl: './model-comparison.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModelComparisonComponent {
  @Input({ required: true }) comparisons: ModelComparison[] = [];

  matchLabel(comparison: ModelComparison): string {
    return comparison.homeTeam && comparison.awayTeam
      ? `${comparison.homeTeam} - ${comparison.awayTeam}`
      : comparison.matchId;
  }

  impactClass(impact: ModelComparison['impactLevel']): string {
    return {
      none: 'bg-slate-800 text-slate-300',
      low: 'bg-emerald-500/10 text-emerald-300',
      medium: 'bg-amber-500/10 text-amber-300',
      high: 'bg-rose-500/10 text-rose-300',
    }[impact];
  }
}
