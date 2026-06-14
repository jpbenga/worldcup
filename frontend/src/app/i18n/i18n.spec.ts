import { describe, expect, it } from 'vitest';
import { COUNTRY_NAMES_FR, countryNameFr } from './country-names.fr';
import { decimalOddsFr, marketLabelFr, marketOutcomeFr } from './market-labels.fr';

describe('French product localization', () => {
  it('covers the 48 tournament teams', () => {
    expect(Object.keys(COUNTRY_NAMES_FR)).toHaveLength(48);
    expect(countryNameFr('Switzerland')).toBe('Suisse');
    expect(countryNameFr('Bosnia & Herzegovina', true)).toBe('Bosnie-Herz.');
  });

  it('translates betting labels and formats decimal odds', () => {
    expect(marketLabelFr('Draw no bet')).toBe('Remboursé si nul');
    expect(marketOutcomeFr('Mexico ou South Africa')).toBe('Mexique ou Afrique du Sud');
    expect(decimalOddsFr(2.4)).toBe('2,40');
  });
});
