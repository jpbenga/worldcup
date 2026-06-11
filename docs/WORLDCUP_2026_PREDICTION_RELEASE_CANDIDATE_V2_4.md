# World Cup 2026 Prediction Release Candidate V2.4

The release candidate packages exactly `72` active `quant_hybrid_v2.2` predictions for frontend consumption. Every match includes fixture metadata, normalized score matrix, top scores, active hybrid 1X2 probabilities, structured secondary markets, confidence and favorite-score coherence.

All 72 matrices, top-score lists and market blocks passed structural validation. `25` matches have a modal-score outcome that differs from the active hybrid 1X2 selection; these are retained and explicitly flagged rather than hidden. No model was retrained and no probability was recalculated by V2.4.

The fixture metadata is a versioned release snapshot, not a live score/status
feed. Consumers must refresh fixture status separately before treating a
scheduled match as not yet started.
