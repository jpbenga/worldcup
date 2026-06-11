import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { Match, MatchPrediction, ModelComparison, ReleaseCandidatePrediction } from '../../models/worldcup.models';
import { ScoreMatrixComponent } from '../score-matrix/score-matrix.component';

@Component({
  selector: 'app-match-modal',
  imports: [DatePipe, PercentPipe, ScoreMatrixComponent],
  templateUrl: './match-modal.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchModalComponent {
  @Input() match?: Match;
  @Input() baseline?: MatchPrediction;
  @Input() elo?: MatchPrediction;
  @Input() comparison?: ModelComparison;
  @Input() activePrediction?: ReleaseCandidatePrediction;
  @Output() closed = new EventEmitter<void>();

  @HostListener('document:keydown.escape')
  close(): void {
    this.closed.emit();
  }
}
