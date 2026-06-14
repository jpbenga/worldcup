import { countryNameFr } from './country-names.fr';

const MARKET_LABELS_FR: Record<string, string> = {
  '1X2': 'Résultat du match (1N2)',
  'Both teams to score': 'Les deux équipes marquent',
  'Double chance': 'Double chance',
  'Draw no bet': 'Remboursé si nul',
  'Over/Under 2.5': 'Plus ou moins de 2,5 buts',
};

export function marketLabelFr(label: string): string {
  return MARKET_LABELS_FR[label] ?? label;
}

export function marketOutcomeFr(label: string): string {
  return label
    .split(/(\s+ou\s+)/i)
    .map((part) => (/^\s+ou\s+$/i.test(part) || part === 'Nul' ? part.toLowerCase() : countryNameFr(part)))
    .join('')
    .replace(/^nul/, 'Nul');
}

export function decimalOddsFr(value: number): string {
  return value.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
