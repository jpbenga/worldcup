import { DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { BacktestResult, Match } from '../../models/worldcup.models';

@Component({
  selector: 'app-prediction-history',
  imports: [DatePipe, PercentPipe],
  templateUrl: './prediction-history.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PredictionHistoryComponent {
  @Input({ required: true }) results: BacktestResult[] = [];
  @Input({ required: true }) matches: Match[] = [];

  matchLabel(matchId: string): string {
    const match = this.matches.find((candidate) => candidate.id === matchId);
    return match ? `${match.homeTeam} - ${match.awayTeam}` : matchId;
  }
}
