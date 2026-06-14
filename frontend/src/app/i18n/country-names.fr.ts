export interface FrenchCountryName {
  full: string;
  short: string;
  code: string;
}

export const COUNTRY_NAMES_FR: Record<string, FrenchCountryName> = {
  Algeria: { full: 'Algérie', short: 'Algérie', code: 'ALG' },
  Argentina: { full: 'Argentine', short: 'Argentine', code: 'ARG' },
  Australia: { full: 'Australie', short: 'Australie', code: 'AUS' },
  Austria: { full: 'Autriche', short: 'Autriche', code: 'AUT' },
  Belgium: { full: 'Belgique', short: 'Belgique', code: 'BEL' },
  'Bosnia & Herzegovina': { full: 'Bosnie-Herzégovine', short: 'Bosnie-Herz.', code: 'BIH' },
  Brazil: { full: 'Brésil', short: 'Brésil', code: 'BRA' },
  Canada: { full: 'Canada', short: 'Canada', code: 'CAN' },
  'Cape Verde Islands': { full: 'Cap-Vert', short: 'Cap-Vert', code: 'CPV' },
  Colombia: { full: 'Colombie', short: 'Colombie', code: 'COL' },
  'Congo DR': { full: 'RD Congo', short: 'RD Congo', code: 'COD' },
  Croatia: { full: 'Croatie', short: 'Croatie', code: 'CRO' },
  Curaçao: { full: 'Curaçao', short: 'Curaçao', code: 'CUW' },
  'Czech Republic': { full: 'Tchéquie', short: 'Tchéquie', code: 'CZE' },
  Ecuador: { full: 'Équateur', short: 'Équateur', code: 'ECU' },
  Egypt: { full: 'Égypte', short: 'Égypte', code: 'EGY' },
  England: { full: 'Angleterre', short: 'Angleterre', code: 'ENG' },
  France: { full: 'France', short: 'France', code: 'FRA' },
  Germany: { full: 'Allemagne', short: 'Allemagne', code: 'GER' },
  Ghana: { full: 'Ghana', short: 'Ghana', code: 'GHA' },
  Haiti: { full: 'Haïti', short: 'Haïti', code: 'HAI' },
  Iran: { full: 'Iran', short: 'Iran', code: 'IRN' },
  Iraq: { full: 'Irak', short: 'Irak', code: 'IRQ' },
  'Ivory Coast': { full: 'Côte d’Ivoire', short: 'Côte d’Ivoire', code: 'CIV' },
  Japan: { full: 'Japon', short: 'Japon', code: 'JPN' },
  Jordan: { full: 'Jordanie', short: 'Jordanie', code: 'JOR' },
  Mexico: { full: 'Mexique', short: 'Mexique', code: 'MEX' },
  Morocco: { full: 'Maroc', short: 'Maroc', code: 'MAR' },
  Netherlands: { full: 'Pays-Bas', short: 'Pays-Bas', code: 'NED' },
  'New Zealand': { full: 'Nouvelle-Zélande', short: 'N.-Zélande', code: 'NZL' },
  Norway: { full: 'Norvège', short: 'Norvège', code: 'NOR' },
  Panama: { full: 'Panama', short: 'Panama', code: 'PAN' },
  Paraguay: { full: 'Paraguay', short: 'Paraguay', code: 'PAR' },
  Portugal: { full: 'Portugal', short: 'Portugal', code: 'POR' },
  Qatar: { full: 'Qatar', short: 'Qatar', code: 'QAT' },
  'Saudi Arabia': { full: 'Arabie saoudite', short: 'Arabie saoudite', code: 'KSA' },
  Scotland: { full: 'Écosse', short: 'Écosse', code: 'SCO' },
  Senegal: { full: 'Sénégal', short: 'Sénégal', code: 'SEN' },
  'South Africa': { full: 'Afrique du Sud', short: 'Afr. du Sud', code: 'RSA' },
  'South Korea': { full: 'Corée du Sud', short: 'Corée du Sud', code: 'KOR' },
  Spain: { full: 'Espagne', short: 'Espagne', code: 'ESP' },
  Sweden: { full: 'Suède', short: 'Suède', code: 'SWE' },
  Switzerland: { full: 'Suisse', short: 'Suisse', code: 'SUI' },
  Tunisia: { full: 'Tunisie', short: 'Tunisie', code: 'TUN' },
  Türkiye: { full: 'Turquie', short: 'Turquie', code: 'TUR' },
  USA: { full: 'États-Unis', short: 'États-Unis', code: 'USA' },
  Uruguay: { full: 'Uruguay', short: 'Uruguay', code: 'URU' },
  Uzbekistan: { full: 'Ouzbékistan', short: 'Ouzbékistan', code: 'UZB' },
};

export const COUNTRY_ALIASES_FR: Record<string, string> = {
  Bosnia: 'Bosnia & Herzegovina',
  'Bosnia and Herzegovina': 'Bosnia & Herzegovina',
  'Cape Verde': 'Cape Verde Islands',
  Curacao: 'Curaçao',
  Czechia: 'Czech Republic',
  'DR Congo': 'Congo DR',
  Turkey: 'Türkiye',
  'United States': 'USA',
};

export function countryNameFr(name: string | null | undefined, compact = false): string {
  if (!name) return '';
  const entry = COUNTRY_NAMES_FR[COUNTRY_ALIASES_FR[name] ?? name];
  return entry ? (compact ? entry.short : entry.full) : name;
}
