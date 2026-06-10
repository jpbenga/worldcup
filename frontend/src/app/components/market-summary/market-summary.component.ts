import { PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { MatchMarkets } from '../../models/worldcup.models';

@Component({
  selector: 'app-market-summary',
  imports: [PercentPipe],
  templateUrl: './market-summary.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MarketSummaryComponent {
  @Input({ required: true }) markets!: MatchMarkets;

  get items(): { label: string; value: number; highlight?: boolean }[] {
    return [
      { label: 'Victoire domicile', value: this.markets.homeWin, highlight: true },
      { label: 'Match nul', value: this.markets.draw },
      { label: 'Victoire extérieur', value: this.markets.awayWin, highlight: true },
      { label: 'Domicile ou nul', value: this.markets.homeOrDraw },
      { label: 'Extérieur ou nul', value: this.markets.awayOrDraw },
      { label: 'Sans nul', value: this.markets.noDraw },
      { label: 'Plus de 1,5 buts', value: this.markets.over15 },
      { label: 'Plus de 2,5 buts', value: this.markets.over25 },
      { label: 'Moins de 2,5 buts', value: this.markets.under25 },
      { label: 'Les deux marquent', value: this.markets.bttsYes },
      { label: 'Au moins une équipe muette', value: this.markets.bttsNo },
    ];
  }
}
