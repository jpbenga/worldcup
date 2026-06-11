# Upstream xG Feature Challenger Design V1.3

## Scope and decision

V1.3 is design-only. It defines isolated upstream expected-goals challengers
for V1.4 and inspects whether the required historical features are available.
It does not implement or train a model, change the active engine, modify World
Cup 2026 predictions, create a combined candidate, or alter
`do_not_promote_yet`.

## Core diagnosis

V1.2 shows that post-probability corrections are not enough. Future
challengers must improve the upstream expected-goals estimates, because the
score matrix and market probabilities are only as good as the xG inputs.

Draw calibration slightly improved test log loss and Brier but degraded
validation and missed the required improvement thresholds. Dixon-Coles rho
substantially reduced modal `1-1` concentration but degraded test log loss and
Brier and increased high-confidence errors. Adjusting probabilities or
low-score mass cannot reliably repair xG estimates that do not represent
competition context, recency, team-strength priors, or sparse-team evidence.

## Available upstream signals

The current expanded historical rows contain match date, season, competition,
`competition_family`, `competition_tier`, `training_weight_hint`, teams and
scores. These fields can support competition weighting, chronological time
decay and low-sample handling. Current Elo ratings and identity mappings exist,
but the ratings are static snapshots rather than historical pre-match values.
Their use on past matches would risk temporal leakage.

V1.4 must publish feature diagnostics before interpreting model results:
coverage by competition and team, recent effective sample sizes, low-sample
flags, missing Elo and mapping behavior, and every temporal-provenance
limitation. The current dataset contains major tournaments and qualifications
but no friendly rows, so the candidate friendly weight cannot be evaluated
until such data exists.

## Challenger C — Competition-Weighted xG

**Objective:** Adapt team strengths and scoring averages to the nature of the
competition.

International competitions have different intensity, selection and scoring
distributions. World Cup, Euro, AFCON, Copa America, qualifiers and friendlies
should not automatically contribute identical evidence.

**V1.4 isolated design:**

- use `competition_tier` and `competition_family`;
- weight training matches by competition comparability;
- retain stronger weight for major tournaments;
- reduce friendlies or less comparable competitions;
- publish aggregate and per-competition results.

Candidate starting parameters:

```json
{
  "major_tournament_weight": 1.0,
  "continental_championship_weight": 0.9,
  "qualifier_weight": 0.75,
  "friendly_weight": 0.4
}
```

Risks include arbitrary weights, amplifying already dominant competitions and
discarding too much useful evidence. Parameter grids must be bounded and
selected on validation only.

## Challenger D — Time-Decay xG

**Objective:** Give more weight to recent evidence.

National-team strength changes with player generations, coaches, injuries and
squad selection. V1.4 should test exponential weighting with half-lives of
`12`, `24`, `36` and `48` months, calculated relative to each predicted
match. No match after the prediction date may contribute. Reports must include
recent coverage and effective sample size by team.

Risks include unstable sparse-team estimates and overfitting to the latest
tournament.

## Challenger E — Elo-Prior xG

**Objective:** Use Elo as a bounded upstream prior or stabilizer, especially
for teams with sparse historical evidence.

The design combines historical attack/defence strength with a bounded Elo
factor, documents missing Elo, and prevents Elo from overwhelming observed
history.

```json
{
  "elo_prior_weight": 0.15,
  "elo_diff_scale": 400,
  "elo_factor_cap": 0.25
}
```

The current Elo source is static and retrieved after the historical matches.
V1.4 should use Elo only if pre-match historical ratings can be sourced or
reconstructed. If only current Elo is available, the challenger must be
explicitly limited, report temporal leakage risk and cannot support promotion.
Other risks are favorite overconfidence and missing identity mappings.

## Challenger F — Low-Sample Fallback xG

**Objective:** Stabilize teams with too little historical evidence.

V1.4 should detect teams below a match threshold, increase smoothing, use a
regional or competition mean when defensible, optionally use a temporally safe
Elo prior, and emit `low_sample_handled`.

```json
{
  "low_sample_threshold": 8,
  "extra_smoothing_weight": 12
}
```

The main risk is oversmoothing genuine differences among smaller teams.
Results must separate low-sample teams from adequately sampled teams.

## Challenger G — Upstream Combined Candidate

The combined candidate is deferred. It may include only C, D, E or F
components that independently pass the V1.4 protocol. It must not be
implemented before isolated causal evidence exists.

## Metrics and guardrails

Each isolated challenger must report 1X2 log loss, Brier, accuracy, average
true-result probability, exact-score and top-3 hit rates, draw and favorite
calibration, modal `1-1`, high-confidence errors, competition segments,
low-sample segments and predicted-versus-actual goals.

A challenger is only promising if test log loss and Brier each improve V0.9
by at least `0.01`, validation supports the direction, draw calibration and
high-confidence safety do not materially regress, modal `1-1` does not become
more concentrated, and no temporal leakage is introduced.

## No-promotion boundary

V1.3 promotes nothing. V1.4 challengers remain isolated experiments selected
on validation and evaluated once on test. Any future promotion requires
separate human validation and explicit authorization before changing the
active engine or World Cup 2026 predictions.
