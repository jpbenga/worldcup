import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { Match, MatchPrediction, ModelComparison } from '../../models/worldcup.models';
import { MarketSummaryComponent } from '../market-summary/market-summary.component';
import { ScoreMatrixComponent } from '../score-matrix/score-matrix.component';

@Component({
  selector: 'app-match-modal',
  imports: [DatePipe, PercentPipe, MarketSummaryComponent, ScoreMatrixComponent],
  templateUrl: './match-modal.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchModalComponent {
  @Input() match?: Match;
  @Input() baseline?: MatchPrediction;
  @Input() elo?: MatchPrediction;
  @Input() comparison?: ModelComparison;
  @Output() closed = new EventEmitter<void>();

  @HostListener('document:keydown.escape')
  close(): void {
    this.closed.emit();
  }
}
