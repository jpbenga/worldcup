import { COUNTRY_ALIASES_FR, COUNTRY_NAMES_FR, countryNameFr } from '../i18n/country-names.fr';

export type RoadToTrophyPayload = any;

const array = (value: any): any[] => (Array.isArray(value) ? value : []);
const object = (value: any): any => (value && typeof value === 'object' ? value : {});
const TEAM_FIELDS = new Set([
  'team', 'name', 'home_team', 'away_team', 'team_a', 'team_b', 'winner', 'projected_winner',
  'opponent', 'active_leader', 'previous_leader',
]);

export function translateRoadPayload(value: any, parentKey = ''): any {
  if (Array.isArray(value)) return value.map((item) => translateRoadPayload(item, parentKey));
  if (typeof value === 'string') {
    return [...Object.keys(COUNTRY_NAMES_FR), ...Object.keys(COUNTRY_ALIASES_FR)]
      .map((source) => [source, countryNameFr(source)] as const)
      .sort(([first], [second]) => second.length - first.length)
      .reduce((text, [source, target]) => text.replaceAll(source, target), value);
  }
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => {
      const translatedKey = parentKey === 'team_paths' ? countryNameFr(key) : key;
      if (TEAM_FIELDS.has(key) && typeof item === 'string') return [translatedKey, countryNameFr(item)];
      return [translatedKey, translateRoadPayload(item, key)];
    }),
  );
}

function qualificationProbability(group: any, team: any): number {
  const probabilities = object(
    team.simulation_probabilities ??
      group.qualification_probabilities?.[team.name] ??
      group.marginal_qualification_probabilities?.[team.name],
  );
  return Number(probabilities.qualification ?? team.qualification_probability ?? 0);
}

export function adaptRoadToTheTrophy(raw: RoadToTrophyPayload): RoadToTrophyPayload {
  const errors: string[] = [];
  const groups = array(raw.groups ?? raw.group_stage?.groups).map((source: any) => {
    const group = object(source);
    const table = array(group.central_table ?? group.centralTable ?? group.standings ?? group.table);
    const matches = array(group.central_matches ?? group.centralMatches ?? group.matches);
    const tableByTeam = new Map(table.map((row: any) => [row.team ?? row.name, row]));
    const teams = array(group.teams).map((sourceTeam: any) => {
      const team = object(sourceTeam);
      const row = object(tableByTeam.get(team.name));
      const qualification = qualificationProbability(group, team);
      return {
        ...team,
        current_rank: Number(team.current_rank ?? row.rank ?? 0),
        played: Number(team.played ?? row.played ?? 0),
        points: Number(team.points ?? row.points ?? 0),
        goal_difference: Number(team.goal_difference ?? row.goal_difference ?? 0),
        goals_for: Number(team.goals_for ?? row.goals_for ?? 0),
        central_status: team.central_status ?? (qualification > 0 ? 'À confirmer' : 'Éliminé'),
        simulation_probabilities: {
          qualification,
          first: Number(team.simulation_probabilities?.first ?? 0),
          second: Number(team.simulation_probabilities?.second ?? 0),
          best_third: Number(team.simulation_probabilities?.best_third ?? 0),
          elimination: Number(team.simulation_probabilities?.elimination ?? 1 - qualification),
        },
      };
    });
    if (teams.length !== 4 || matches.length === 0) {
      errors.push(`Groupe ${group.group ?? '?'} incomplet: ${teams.length} équipes, ${matches.length} matchs.`);
    }
    return {
      ...group,
      teams,
      matches,
      central_table: table,
      central_matches: matches,
      qualification_probabilities:
        group.qualification_probabilities ?? group.qualificationProbabilities ?? group.marginal_qualification_probabilities ?? {},
    };
  });
  const rounds = array(raw.rounds);
  if (groups.length !== 12) errors.push(`${groups.length} groupes disponibles au lieu de 12.`);
  if (rounds.length !== 5) errors.push(`${rounds.length} tours knockout disponibles au lieu de 5.`);
  return translateRoadPayload({
    ...raw,
    groups,
    rounds,
    ui_contract_valid: errors.length === 0,
    ui_contract_errors: errors,
  });
}
