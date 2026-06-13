# Active 2026 Release Candidate Strategy V2.4

V2.4 advances the main product roadmap instead of creating a V2.3.1 reporting micro-iteration. V2.2 established the quant engine on refreshed historical evidence, and the user accepted it as the active engine. V2.3 then showed where matrix-derived markets are useful and where their limitations must remain visible.

The active engine is no longer experimental. V2.4 treats quant_hybrid_v2.2 as the active release-candidate engine unless validation proves that active prediction files are missing or inconsistent.

V2.4 consolidates the 72 active predictions into a frontend-oriented release candidate, integrates the secondary-market performance summary as product transparency, verifies active-file consistency, and runs the first group-stage tournament simulation. It does not retune, retrain or rerun Optuna.

The deliverables are versioned generated JSON, matching snapshots and frontend assets, plus contracts for match lists, match detail, score matrices, markets, group simulation and transparency screens. Knockout simulation is deliberately excluded until a real bracket or fixture structure is available.
