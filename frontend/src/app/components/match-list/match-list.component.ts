import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { Match, MatchPrediction } from '../../models/worldcup.models';
import { MatchCardComponent } from '../match-card/match-card.component';

@Component({
  selector: 'app-match-list',
  imports: [MatchCardComponent],
  templateUrl: './match-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatchListComponent {
  @Input({ required: true }) predictions: MatchPrediction[] = [];
  @Input({ required: true }) matches: Match[] = [];
  @Output() predictionSelected = new EventEmitter<MatchPrediction>();

  matchFor(matchId: string): Match | undefined {
    return this.matches.find((match) => match.id === matchId);
  }
}
