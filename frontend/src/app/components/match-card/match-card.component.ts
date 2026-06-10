import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { Match, MatchPrediction } from '../../models/worldcup.models';
import { DataSourceBadgeComponent } from '../data-source-badge/data-source-badge.component';

@Component({
  selector: 'app-match-card',
  imports: [DatePipe, PercentPipe, DataSourceBadgeComponent],
  templateUrl: './match-card.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchCardComponent {
  @Input({ required: true }) prediction!: MatchPrediction;
  @Input() match?: Match;
  @Output() viewDetail = new EventEmitter<MatchPrediction>();

  get title(): string {
    return this.match ? `${this.match.homeTeam} - ${this.match.awayTeam}` : this.prediction.matchId;
  }

  get signal(): string {
    return [
      { label: 'Victoire domicile', value: this.prediction.markets.homeWin },
      { label: 'Match nul', value: this.prediction.markets.draw },
      { label: 'Victoire extérieur', value: this.prediction.markets.awayWin },
    ].sort((first, second) => second.value - first.value)[0].label;
  }

  confidenceClass(): string {
    return {
      low: 'bg-rose-500/10 text-rose-300 border-rose-500/20',
      medium: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
      high: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
    }[this.prediction.confidence];
  }
}
