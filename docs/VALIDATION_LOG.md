# Validation Log

## V0.2 / V0.2.1 — Data Foundation + Manual Validation Checklists

Date: 2026-06-10
Validator: Jeanpaul Benga
Commit: `e3913e7 Add manual validation checklists`

### Technical validation

- [x] Backend pipeline passed
- [x] JSON snapshots generated
- [x] Backend snapshots match Angular assets
- [x] Angular build passed
- [x] Angular tests passed
- [x] Forbidden artifacts check passed
- [x] Data provenance files present
- [x] Mock data clearly identified as non-real data

### Manual visual validation

- [ ] Home page checked
- [ ] Data status section checked
- [ ] Provenance badges checked
- [ ] Match cards checked
- [ ] Prediction probabilities checked
- [ ] Score matrix checked
- [ ] Market summary checked
- [ ] Prediction history checked
- [ ] Responsible notice checked
- [ ] Browser console checked
- [ ] Network JSON HTTP 200 checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Technical checks completed on 2026-06-10. The backend pipeline generated all
expected snapshots, JSON validation passed, backend snapshots matched Angular
assets, and the Angular build and tests passed with Node `22.22.3`.

The broad forbidden-artifacts command returned
`backend/scripts/build_snapshots.py` because its filename contains `build`.
A path-aware check confirmed that no forbidden build directory or artifact is
tracked.

Manual visual validation still requires human review before moving to V0.3.

### Issues to fix before next phase

- Complete the manual visual validation checklist and record the human decision.

## V0.3.1 — Team Identity Mapping

Date: 2026-06-10
Validator: Jeanpaul Benga
Commit: `8254b2b Add team identity mapping for API-Football and Elo`

### Technical validation

- [x] `build_team_identity_map.py` passed
- [x] `validate_team_mappings.py` passed
- [x] `team_identity_map.json` present
- [x] `team_aliases.json` present
- [x] `unmapped_teams.json` present
- [x] `team_mapping_report.json` present
- [x] `team_mapping_status.json` present
- [x] API-Football teams count checked
- [x] Elo teams count checked
- [x] coverage checked
- [x] duplicate checks passed
- [x] `build_snapshots.py` passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] secret scan passed
- [x] forbidden artifacts check passed

### Mapping summary

```text
API-Football teams: 48
Elo teams: 244
Mapped: 48
Auto validated: 48
Needs review: 0
Unmapped API teams: 0
Coverage: 100 %
Status: PASS
Exact mappings: 42
Alias mappings: 6
```

### Alias mappings requiring human review

```text
1. API-Football: Czech Republic → Elo: Czechia | code: CZE | method: alias | confidence: 0.98 | Elo: 1740, rank: 35
2. API-Football: Türkiye → Elo: Turkey | code: TUR | method: alias | confidence: 0.98 | Elo: 1911, rank: 13
3. API-Football: Bosnia & Herzegovina → Elo: Bosnia and Herzegovina | code: BIH | method: alias | confidence: 0.98 | Elo: 1595, rank: 65
4. API-Football: Congo DR → Elo: DR Congo | code: CGO | method: alias | confidence: 0.98 | Elo: 1652, rank: 55
5. API-Football: Cape Verde Islands → Elo: Cape Verde | code: CPV | method: alias | confidence: 0.98 | Elo: 1578, rank: 68
6. API-Football: USA → Elo: United States | code: USA | method: alias | confidence: 0.98 | Elo: 1726, rank: 38
```

### Manual visual validation

- [ ] Alias mappings checked manually
- [ ] Sensitive aliases checked
- [ ] Elo ratings association checked
- [ ] Angular mapping summary checked
- [ ] Documentation checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Technical validation completed on 2026-06-10. Mapping generation, structural
validation, JSON checks, duplicate checks, snapshot generation, Angular build
and Angular tests passed.

The broad forbidden-artifacts command returned
`backend/scripts/build_snapshots.py` and
`backend/scripts/build_team_identity_map.py` because their filenames contain
`build`. A path-aware tracked-files check confirmed that no forbidden build
directory or artifact is versioned.

The secret scan returned expected source-code references to
`API_FOOTBALL_KEY` and `x-apisports-key`. A fixed-string scan confirmed that
the real API key has zero tracked matches.

Manual validation still requires human review before integrating Elo into the
prediction model.

### Issues to fix before next phase

- To be completed after human review.
