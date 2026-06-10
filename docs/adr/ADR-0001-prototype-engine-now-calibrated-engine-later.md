# ADR-0001 — Prototype engine now, calibrated engine later

Status: Accepted

Date: 2026-06-10

## Context

API-Football real fixtures and the grouped review UX are working. The current
engine is deliberately simple and replaceable. V0.5.1 confirms `1-1` as the
modal score for `72/72` baseline fixtures and for all Elo variants because the
baseline xG are neutral `1.35 / 1.35`.

The user wants to continue validating the product workflow while preparing a
future historically calibrated engine. The repository contains reusable
Poisson/Dixon-Coles, market and Elo-related components, but no trustworthy
trained historical engine or validated historical parameter set.

## Decision

- Keep the Prototype Prediction Engine for the current workflow.
- Do not present it as trained or historically calibrated.
- Do not force artificial prediction diversity.
- Preserve the published snapshot contracts as the replacement boundary.
- Keep the UI warning and future-fixture `not_evaluable` backtesting status.
- Prepare a future historical dataset and calibrated engine in separate phases.
- Do not restore the sensitive and tightly coupled `drc-prototype/` directory.

## Consequences

- Current predictions are useful for workflow testing, not robust forecasting.
- Uniform modal scores remain visible until validated inputs replace neutral xG.
- Future work focuses first on historical data acquisition and chronology.
- A replacement model must prove out-of-sample performance and calibration.
- Model migration can occur behind stable JSON contracts with explicit versions.
- V0.7 should be a historical data acquisition spike, not a model rewrite.
