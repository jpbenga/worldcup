import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Match, MatchPrediction } from '../../models/worldcup.models';
import { MarketSummaryComponent } from '../market-summary/market-summary.component';
import { ScoreMatrixComponent } from '../score-matrix/score-matrix.component';
import { DataSourceBadgeComponent } from '../data-source-badge/data-source-badge.component';

@Component({
  selector: 'app-match-detail',
  imports: [DatePipe, PercentPipe, DataSourceBadgeComponent, MarketSummaryComponent, ScoreMatrixComponent],
  templateUrl: './match-detail.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchDetailComponent {
  @Input({ required: true }) prediction!: MatchPrediction;
  @Input() match?: Match;
}
