# Matchday Workspace Policy V2.18

Les réponses API brutes et caches locaux représentent les sources récupérées. Les fichiers `generated/` sont les sorties canoniques calculées; `snapshots/` conserve les copies reproductibles; `frontend/src/assets/data/` contient les contrats consommés par Angular. Les manifests et validations expliquent comment ces sorties ont été produites.

Un refresh local peut modifier beaucoup de fichiers suivis. Ces changements ne doivent jamais être ajoutés implicitement avec `git add .`. Ils doivent être examinés, classés et commités uniquement dans une livraison Matchday explicite. Les fichiers temporaires, `.env`, secrets, builds, dépendances et environnements virtuels restent locaux ou ignorés.

L’audit V2.18 classe les fichiers sales comme refresh attendu ou changement hors scope et recommande une revue avant commit. Il ne supprime ni ne restaure rien automatiquement. Les artefacts V2.18 propres peuvent être versionnés séparément des sorties Matchday locales.
