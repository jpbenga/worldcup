# Creative Tournament Experience Strategy V2.11

## Product ambition

`/simulation` should be a strong product feature because it is the place where
individual match probabilities become a readable tournament story. The route
must answer the questions people naturally ask: who leads the campaign proxy,
which contenders are stable, which groups are open, what changed after real
results, and how a less conservative alternative changes the picture.

The page should not become a dashboard full of dense tables. V2.11 uses a
progressive narrative: a leader hero, a projected-campaign path, contender
cards, group storylines, locked-result moments and a clearly secondary
active-versus-alternative comparison. The existing detailed group explorer
remains available below those story blocks.

## Available evidence

V2.11 composes existing result-aware artifacts rather than generating new
predictions. The V2.10 refresh manifest provides recency and match-state
counts. Conditioned active and candidate simulations provide group
qualification probabilities. Projected campaigns provide contender proxy
scores. Live standings and results provide current reality. V2.9 comparisons
provide team movement, affected groups and score-matrix differences.

The operational V2.10 refresh remains the upstream source of truth. A routine
refresh can update every underlying result-aware layer; the V2.11 builder then
regenerates only the creative product aggregate. It does not train the model,
rerun Optuna, modify active probabilities or promote the candidate.

## Honest tournament leader

The strongest active projected-campaign proxy becomes the **Favori projeté**
and **leader de campagne**. Stability against the alternative projection,
qualification probability, group-winner probability and contender proxy rank
provide context. This is an editorial hierarchy over existing evidence, not a
new trophy probability.

The projected champion is a campaign proxy while the official knockout bracket is unavailable. It must not be labelled as a fully simulated World Cup champion.

When the official knockout bracket is unavailable, the UI must say
`Proxy non officiel`, `Projection de campagne` and `Bracket officiel
indisponible`. It must not claim a predicted champion, official path or full
World Cup simulation. No opponent or pairing is invented.

## Active and alternative projections

The active prediction always remains the default and official product
forecast. The alternative is labelled `Projection alternative non active` and
is used as a scenario lens: it shows what changes when score distributions are
less conservative. Leader stability, team rises and falls, affected groups and
modal-score changes are presented as comparative evidence.

The comparison should explain differences without implying that the
alternative supersedes the active engine. A toggle controls the detailed group
view, while a concise side-by-side story block explains the wider effect.

## Creative but readable UX

The page opens with one decisive story, then progressively reveals the
campaign, contenders and volatile groups. Color communicates meaning:
cyan for active, violet for alternative, emerald for locked reality, amber for
uncertainty and limitations. Compact cards replace large summary tables.

The existing group table remains because it is useful for deliberate
exploration, but it comes after the story layer. Match cards, group views and
modals remain unchanged. This keeps V2.11 focused, recognizable and honest
while making `/simulation` feel like a living tournament feature.
