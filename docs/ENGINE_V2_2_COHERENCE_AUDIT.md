# Engine V2.2 Coherence Audit

The product audit compares the hybrid 1X2 favorite with the outcome implied by the modal Poisson score. A clear favorite has an outcome-probability lead of at least 0.08.

- Modal 1-1 test rate: `23.7%`
- Clear-favorite alignment: `82.3%`
- Favorites with modal 1-1: `21.5%`
- Product satisfactory: `true`

The guardrails require a marked reduction from V2.0's 47.5% modal 1-1 rate and at least 55% clear-favorite alignment.

Misaligned clear-favorite examples remain in the JSON artifact for manual
review; aggregate success does not remove the need to inspect product-facing
contradictions.
