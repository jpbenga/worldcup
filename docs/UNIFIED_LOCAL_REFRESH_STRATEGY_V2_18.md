# Unified Local Refresh Strategy V2.18

Un refresh partiel rend le produit incohérent : les résultats peuvent être récents tandis que la transparence, les standings ou Road to the Trophy restent basés sur un état antérieur. Un nouveau score officiel doit donc reconstruire toutes les couches qui l’utilisent, jusqu’aux assets lus par Angular.

V2.18 crée un orchestrateur local Python unique. Le frontend ne contacte jamais API-Football et ne reçoit jamais la clé API. L’orchestrateur détecte d’abord si un travail est nécessaire, puis appelle le pipeline Matchday existant, la transparence, SimuAI Tournament Engine V3, le view model officiel, la fraîcheur et les validations. Il ne réentraîne pas `quant_hybrid_v2.2` et ne relance pas Optuna.

No public page should consume data older than the official results integrated in the local refresh. Le système reste idempotent : si les résultats, versions, validations, assets et nombre de simulations sont cohérents, la simulation lourde peut être sautée.
