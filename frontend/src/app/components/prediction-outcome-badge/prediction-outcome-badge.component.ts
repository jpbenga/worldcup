import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

export type PredictionOutcomeState = 'success' | 'partial' | 'fail' | 'push' | 'pending' | 'neutral';

@Component({
  selector: 'app-prediction-outcome-badge',
  templateUrl: './prediction-outcome-badge.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PredictionOutcomeBadgeComponent {
  @Input({ required: true }) label = '';
  @Input({ required: true }) state: PredictionOutcomeState = 'neutral';
  @Input() detail = '';

  get icon(): string {
    return {
      success: '✓',
      partial: '≈',
      fail: '×',
      push: '↔',
      pending: '…',
      neutral: '•',
    }[this.state];
  }

  get classes(): string {
    return {
      success: 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200',
      partial: 'border-cyan-500/35 bg-cyan-500/10 text-cyan-200',
      fail: 'border-rose-500/35 bg-rose-500/10 text-rose-200',
      push: 'border-amber-500/35 bg-amber-500/10 text-amber-200',
      pending: 'border-slate-700 bg-slate-800/70 text-slate-300',
      neutral: 'border-slate-700 bg-slate-900 text-slate-300',
    }[this.state];
  }
}
