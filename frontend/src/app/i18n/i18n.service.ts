import { Injectable } from '@angular/core';
import { countryNameFr } from './country-names.fr';
import { decimalOddsFr, marketLabelFr, marketOutcomeFr } from './market-labels.fr';

@Injectable({ providedIn: 'root' })
export class I18nService {
  team(name: string | null | undefined, compact = false): string {
    return countryNameFr(name, compact);
  }

  referenceOdds(payload: any): any {
    return {
      ...payload,
      fixtures: (payload?.fixtures ?? []).map((fixture: any) => ({
        ...fixture,
        match_label: fixture.match_label?.split(' vs ').map((name: string) => this.team(name)).join(' contre '),
        markets: (fixture.markets ?? []).map((market: any) => ({
          ...market,
          market_label: marketLabelFr(market.market_label),
          outcomes: (market.outcomes ?? []).map((outcome: any) => ({
            ...outcome,
            label: marketOutcomeFr(outcome.label),
            odds_label: decimalOddsFr(outcome.odds),
          })),
        })),
      })),
    };
  }
}
