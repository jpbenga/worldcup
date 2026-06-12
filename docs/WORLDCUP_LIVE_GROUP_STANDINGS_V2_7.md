# World Cup Live Group Standings V2.7

V2.7 builds all 12 group tables exclusively from `1` finished official result(s). Unplayed and live matches do not award points. Each row exposes played, wins, draws, losses, goals for, goals against, goal difference, points and rank.

Current Group A: `[{'team': 'Mexico', 'played': 1, 'wins': 1, 'draws': 0, 'losses': 0, 'goals_for': 2, 'goals_against': 0, 'goal_difference': 2, 'points': 3, 'rank': 1}, {'team': 'Czech Republic', 'played': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0, 'rank': 2}, {'team': 'South Korea', 'played': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0, 'rank': 3}, {'team': 'South Africa', 'played': 1, 'wins': 0, 'draws': 0, 'losses': 1, 'goals_for': 0, 'goals_against': 2, 'goal_difference': -2, 'points': 0, 'rank': 4}]`.

The current ordering uses points, goal difference, goals scored and team name as a deterministic fallback. Full FIFA head-to-head, fair-play and drawing-of-lots tiebreakers are documented as unavailable until they are necessary and supported by complete data. Pre-match predictions are not used to build standings.
