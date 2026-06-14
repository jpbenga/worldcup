import { describe, expect, it } from 'vitest';
import { adaptRoadToTheTrophy } from './road-to-the-trophy.adapter';

describe('adaptRoadToTheTrophy', () => {
  it('normalizes historical group field variants', () => {
    const groups = Array.from({ length: 12 }, (_, index) => ({
      group: String.fromCharCode(65 + index),
      teams: ['A', 'B', 'C', 'D'].map((name, teamIndex) => ({ name: `${name}${index}`, qualification_probability: 0.5 })),
      central_table: ['A', 'B', 'C', 'D'].map((name, teamIndex) => ({
        team: `${name}${index}`,
        rank: teamIndex + 1,
        played: 3,
        points: 6 - teamIndex,
        goal_difference: 2 - teamIndex,
        goals_for: 4,
      })),
      central_matches: [{ match_id: `m${index}` }],
    }));
    const adapted = adaptRoadToTheTrophy({ groups, rounds: Array.from({ length: 5 }, () => ({ matches: [] })) });
    expect(adapted.ui_contract_valid).toBe(true);
    expect(adapted.groups[0].teams[0].goals_for).toBe(4);
    expect(adapted.groups[0].matches).toHaveLength(1);
  });

  it('marks an incomplete group instead of silently rendering it', () => {
    const adapted = adaptRoadToTheTrophy({ groups: [{ group: 'A', teams: [], matches: [] }], rounds: [] });
    expect(adapted.ui_contract_valid).toBe(false);
    expect(adapted.ui_contract_errors.length).toBeGreaterThan(0);
  });
});
