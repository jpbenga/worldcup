import { DatePipe, KeyValuePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DualMatrixComparison, MatchPrediction, MatchState, ModelComparison } from '../../models/worldcup.models';
import { ScoreMatrixComponent } from '../score-matrix/score-matrix.component';

@Component({
  selector: 'app-match-modal',
  imports: [DatePipe, KeyValuePipe, PercentPipe, RouterLink, ScoreMatrixComponent],
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
}
