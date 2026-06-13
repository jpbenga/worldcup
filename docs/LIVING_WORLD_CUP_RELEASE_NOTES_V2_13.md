# Living World Cup Bracket & Scenario Engine Release Notes V2.13

V2.13 transforme `/simulation` en **Chemin vers le trophée**. La page commence
par le Vainqueur projeté, la finale projetée et le contexte des résultats
officiels. Elle affiche ensuite les 16es, 8es, quarts, demies et finale dans un
bracket horizontal utilisable sur mobile grâce au défilement.

Le moteur de scénario utilise les probabilités issues des 50 000 simulations
conditionnées pour sélectionner 32 qualifiés projetés, construire un tableau
dérivé et simuler 50 000 parcours à élimination directe. Les 72 matchs de
groupes connus et les 32 slots projetés documentent la cible de 104 matchs. Le
bracket officiel étant indisponible, chaque appariement est marqué Projeté et
À confirmer.

La home retire les informations techniques de provenance, d'exploration et de
backtest. SimuAI devient le nom public du moteur. Score recommandé, Prono IA,
Résultat officiel et Bilan du prono remplacent le jargon interne.

Les groupes disposent maintenant d'une navigation par journées. Les cards et
la modal s'adaptent au statut du match. La variante expérimentale quitte le
centre de l'expérience et reste disponible uniquement dans un Mode labo
replié.

V2.13 ne modifie aucune prédiction d'avant-match, ne promeut aucune variante,
ne réentraîne aucun modèle et ne relance pas Optuna.
