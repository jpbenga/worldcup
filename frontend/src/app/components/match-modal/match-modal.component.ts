import { DatePipe, KeyValuePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DualMatrixComparison, MatchPrediction, MatchState, ModelComparison } from '../../models/worldcup.models';
import { ScoreMatrixComponent } from '../score-matrix/score-matrix.component';
import { PredictionOutcomeBadgeComponent, PredictionOutcomeState } from '../prediction-outcome-badge/prediction-outcome-badge.component';

@Component({
  selector: 'app-match-modal',
  imports: [DatePipe, KeyValuePipe, PercentPipe, PredictionOutcomeBadgeComponent, RouterLink, ScoreMatrixComponent],
  templateUrl: './match-modal.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchModalComponent {
  @Input() baseline?: MatchPrediction;
  @Input() elo?: MatchPrediction;
  @Input() comparison?: ModelComparison;
  @Input() state?: MatchState;
  @Input() dualMatrix?: DualMatrixComparison;
  @Output() closed = new EventEmitter<void>();

  @HostListener('document:keydown.escape')
  close(): void {
    this.closed.emit();
  }

  booleanState(value?: boolean, partial = false): PredictionOutcomeState {
    if (value === undefined) return 'pending';
    if (!value) return 'fail';
    return partial ? 'partial' : 'success';
  }

  dnbState(value?: string): PredictionOutcomeState {
    if (!value) return 'pending';
    if (value === 'win') return 'success';
    if (value === 'push') return 'push';
    return value === 'loss' ? 'fail' : 'neutral';
  }

  dnbLabel(value?: string): string {
    return { win: 'Réussi', loss: 'Raté', push: 'Remboursé', not_applicable: 'Non applicable' }[value ?? ''] ?? 'En attente';
  }

  summaryState(state: MatchState): PredictionOutcomeState {
    if (state.evaluation.exactScoreHit) return 'success';
    if (state.evaluation.oneXTwoHit || state.evaluation.top3Hit || state.evaluation.top5Hit) return 'partial';
    return 'fail';
  }

  summaryLabel(state: MatchState): string {
    if (state.evaluation.exactScoreHit) return 'Score exact trouvé';
    if (state.evaluation.oneXTwoHit) return 'Bon résultat, score différent';
    if (state.evaluation.top3Hit || state.evaluation.top5Hit) return 'Score présent dans la sélection';
    return 'Prono raté';
  }
}
